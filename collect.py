# -*- coding: utf-8 -*-
"""GLOBAL DEAL HUNTER — collector.

Fetches every configured feed, normalises items into deal rows, classifies
category / price-type / region / deadline, scores, stores in SQLite.

Ground rules (from the brief):
  * never invent a field — if the text does not say it, the column stays empty
  * a price is not a saving; value is only recorded from reward phrasing
  * price_type separates free / trial / topup / volume / invite
"""
import argparse, hashlib, html, os, re, socket, sys, time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import SOURCES
import classify, dates
import db as store

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HDRS = {"User-Agent": UA,
        "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.5",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8"}
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def _proxy():
    env = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") \
        or os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
    if env:
        return env
    s = socket.socket(); s.settimeout(0.4)
    try:
        s.connect(("127.0.0.1", 3128)); return "http://127.0.0.1:3128"
    except OSError:
        return None
    finally:
        s.close()


def _opener():
    h = []
    p = _proxy()
    if p:
        h.append(urllib.request.ProxyHandler({"http": p, "https": p}))
    return urllib.request.build_opener(*h)


OP = _opener()


def fetch(url, tries=3, timeout=25):
    """GET with backoff. 429 means the host is rate limiting us, not that the
    feed broke, so wait far longer before the next try."""
    last = None
    for i in range(tries):
        try:
            with OP.open(urllib.request.Request(url, headers=HDRS), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            code = getattr(e, "code", None)
            if i < tries - 1:
                time.sleep(8.0 if code == 429 else 1.5 * (i + 1))
    raise last


def clean(s, limit=420):
    if not s:
        return ""
    s = WS_RE.sub(" ", html.unescape(TAG_RE.sub(" ", s))).strip()
    return s[:limit]


def _find(el, name):
    f = el.find(name)
    return f if f is not None else el.find("{*}" + name)


def _text(el, *names):
    for n in names:
        f = _find(el, n)
        if f is not None and (f.text or "").strip():
            return f.text.strip()
    return ""


def parse_feed(raw):
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        i = raw.find(b"<")
        try:
            root = ET.fromstring(raw[i:])
        except Exception:
            return []
    out = []
    for el in root.iter():
        if el.tag.split("}")[-1] not in ("item", "entry"):
            continue
        title = clean(_text(el, "title"), 300)
        link = _text(el, "link")
        if not link:
            for l in el.findall(".//{*}link"):
                if l.get("href"):
                    link = l.get("href"); break
        if not link:
            guid = _text(el, "guid", "id")
            if guid.startswith("http"):
                link = guid
        body = clean(_text(el, "description", "summary", "content", "encoded"), 700)
        if not body:
            c = _find(el, "content")
            if c is not None:
                body = clean("".join(c.itertext()), 700)
        src_name = _text(el, "source")
        if title and link:
            out.append(dict(title=title, link=link, body=body, source=src_name,
                            published=_text(el, "pubDate", "published", "updated", "date")))
    return out


MAX_AGE_DAYS = 45


def parse_binance(raw):
    """Binance CMS announcement list -> items.

    The public announcement API answers the box with real campaign copy
    (HODLer airdrops, referral tournaments, launchpool) where the RSS
    endpoints are 405/301. Dates arrive as ms epochs under releaseDate.
    """
    import json
    out = []
    try:
        doc = json.loads(raw)
    except Exception:
        return out
    arts = ((doc.get("data") or {}).get("articles")) or []
    for a in arts:
        title = (a.get("title") or "").strip()
        if not title:
            continue
        ts = a.get("releaseDate")
        pub = ""
        if ts:
            try:
                pub = datetime.fromtimestamp(ts / 1000.0, timezone.utc).strftime(
                    "%a, %d %b %Y %H:%M:%S +0000")
            except Exception:
                pub = ""
        code = a.get("code") or ""
        out.append(dict(title=title,
                        link="https://www.binance.com/en/support/announcement/detail/" + code,
                        body="", published=pub, source="Binance", detail_code=code))
    return out


BINANCE_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binance_dates.json")


def _load_cache():
    try:
        import json
        return json.load(open(BINANCE_CACHE, encoding="utf-8"))
    except Exception:
        return {}


def enrich_binance(items, c, cap=12, pause=0.7):
    """Fill published for unseen Binance rows from the article detail API.

    The list endpoint carries no date, so each row needs a detail call; the
    API answers 429 when those arrive in a burst, so dates are cached on
    disk per article code and calls are spaced out. A row we still cannot
    date is dropped rather than shown undated, because an undated item never
    ages out of the board.
    """
    import json
    cache = _load_cache()
    dirty = False
    done = 0
    for it in items:
        if it.get("published"):
            continue
        code = it.get("detail_code")
        if not code:
            continue
        if code in cache:
            it["published"] = cache[code]
            continue
        if done >= cap:
            continue
        try:
            raw = fetch("https://www.binance.com/bapi/composite/v1/public/cms/article/"
                        "detail/query?articleCode=" + code, tries=2)
            ts = (json.loads(raw).get("data") or {}).get("publishDate")
            done += 1
            if ts:
                pub = datetime.fromtimestamp(ts / 1000.0, timezone.utc).strftime(
                    "%a, %d %b %Y %H:%M:%S +0000")
                it["published"] = pub
                cache[code] = pub
                dirty = True
        except Exception:
            done += 1
        time.sleep(pause)
    if dirty:
        try:
            json.dump(cache, open(BINANCE_CACHE, "w", encoding="utf-8"))
        except Exception:
            pass
    return [it for it in items if it.get("published")]


def fresh(published, days=MAX_AGE_DAYS):
    """News feeds carry years of archive — OpenAI News returned 1372 items back
    to 2021, which put a dead 'DALL·E beta' post at rank 5. Deal feeds often omit
    a date entirely, so an undated item is kept and a dated stale one is dropped."""
    if not published:
        return True
    p = published.strip().replace("GMT", "+0000")
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M %z",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d",
                "%a, %d %b %Y %H:%M:%S"):
        try:
            dt = datetime.strptime(p, fmt)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days <= days
    return True


def fingerprint(title):
    """Stable id for an offer.

    Titles are normalised first — case, punctuation, bracketed qualifiers like
    "[YMMV]" and "Reg $100.00" tails — so the same offer reposted with a
    different vendor's garnish does not enter twice.
    """
    t = (title or "").lower()
    t = re.sub(r"\[[^\]]{0,20}\]|\([^)]{0,20}\)", " ", t)
    t = re.sub(r"\b(?:reg|regular|was|now|ymmv|dp|sd|expired|dead|off)\b", " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return hashlib.sha1(t[:120].encode("utf-8")).hexdigest()[:16]


def score_deal(price_type, usd, deadline, weight, native):
    # A deal that costs money up front is not worth more than a free one just
    # because the headline figure is large; the $ figure is added below.
    s = {"free": 30.0, "trial": 20.0, "deposit": 12.0, "spend": 10.0,
         "topup": 10.0, "volume": 6.0, "invite": 4.0}.get(price_type, 5.0)
    if usd:
        s += min(40.0, usd / 5.0)
    if deadline:
        try:
            d = datetime.strptime(deadline, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days = (d - datetime.now(timezone.utc)).days
            s += 12 if 0 <= days <= 3 else 9 if days <= 14 else 3 if days > 14 else 0
        except ValueError:
            pass
    return round(s + 10.0 * (weight or 1.0) + (6.0 if native else 0.0), 1)


def allowed(src, it):
    """Per-source admission. A query feed is OR-ish at the server, so it needs a
    must-match on the title; a news feed needs an explicit offer and fresh date."""
    title = it["title"]
    for pat in src.get("must") or ():
        if re.search(pat, title, re.I):
            break
    else:
        if src.get("must"):
            return False
    for dom in src.get("deny") or ():
        if dom in (it.get("link") or "") or dom in (it.get("source") or "").lower():
            return False
    ok, _ = classify.in_scope(title, it["body"])
    if not ok:
        return False
    # Editorial/closed-offer markers disqualify an item on every feed: a deal
    # feed still carries "airdrop distribution completed" bookkeeping.
    if not classify.passes_gate_noise(title):
        return False
    # Staleness is per source, not global: a bank bonus posted in January is
    # still claimable in November, while a Slickdeals price is dead in a week.
    # An undated item is kept; merchant deal feeds rarely publish dates.
    if it.get("published") and not fresh(it["published"], src.get("max_age", MAX_AGE_DAYS)):
        return False
    if not src["native"]:
        if not classify.passes_gate(title, it["body"]):
            return False
    return True


def build(src, it):
    title, body = it["title"], it["body"]
    if not allowed(src, it):
        return None
    ptype = classify.price_type(title, body)
    if ptype == "unknown" and src.get("sale"):
        # On a merchant sale feed an unstated condition means "on sale" — but a
        # bank post with no stated condition must stay 未标注, not become a discount.
        ptype = "discount"
    val, usd = classify.value(title, body)
    deadline = dates.find(title, body)
    return dict(
        fp=fingerprint(title),
        title=title,
        # A keyword feed's own category is only a guess; if no rule fires, the
        # item is not filed under the query's topic ("云主机" once caught WoW).
        category=classify.category(title, body,
                                   "other" if src.get("sale") else src["category"]),
        summary=body[:400],
        value=val, value_usd=usd,
        requirements=classify.requirements(title, body),
        region=classify.region(title, body),
        starts_at=None,
        ends_at=deadline,
        steps="",
        official_url=it["link"],
        source_name=src["name"], source_url=src["url"],
        price_type=ptype,
        risk=classify.risks(title, body),
        score=score_deal(ptype, usd, deadline, src["weight"], src["native"]),
    )


def run(verbose=True):
    started = int(time.time())
    c = store.conn()
    fetched = ins = upd = 0
    errors = []
    for src in SOURCES:
        try:
            raw = fetch(src["url"])
            items = parse_binance(raw) if src.get("kind") == "json" else parse_feed(raw)
            if src.get("kind") == "json" and src.get("detail_dates"):
                items = enrich_binance(items, c)
        except Exception as e:
            errors.append("%s: %s" % (src["name"], e))
            if verbose:
                print("  !! %-34s %s" % (src["name"], str(e)[:80]))
            continue
        fetched += len(items)
        kept = 0
        for it in items:
            try:
                d = build(src, it)
            except Exception as e:
                errors.append("%s build: %s" % (src["name"], e)); continue
            if not d:
                continue
            kept += 1
            r = store.upsert_deal(c, d, started)
            ins += (r == "insert"); upd += (r == "update")
        c.commit()
        if verbose:
            print("  %-34s items=%-5d kept=%d" % (src["name"], len(items), kept))
    expired = store.expire(c, started)
    c.execute("INSERT INTO run(started,finished,fetched,inserted,updated,errors) VALUES(?,?,?,?,?,?)",
              (started, int(time.time()), fetched, ins, upd, "\n".join(errors[:40])))
    c.commit(); c.close()
    print("\nrun done: fetched=%d new=%d refreshed=%d expired=%d errors=%d"
          % (fetched, ins, upd, expired, len(errors)))
    return dict(fetched=fetched, inserted=ins, updated=upd, expired=expired, errors=errors)


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    run()
