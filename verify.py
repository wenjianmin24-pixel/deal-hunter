# -*- coding: utf-8 -*-
"""Link verification — the part that decides whether this thing is real.

For every active deal, fetch its official link with a real browser UA and store
the HTTP status + final URL. A deal whose link 404s or is unreachable is NOT
silently kept: it is marked so the dashboard can show it was checked and failed.
"""
import argparse, os, socket, sys, time
import urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db as store

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HDRS = {"User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8"}


def _opener():
    h = []
    env = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") \
        or os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
    proxy = env
    if not proxy:
        s = socket.socket(); s.settimeout(0.4)
        try:
            s.connect(("127.0.0.1", 3128)); proxy = "http://127.0.0.1:3128"
        except OSError:
            proxy = None
        finally:
            s.close()
    if proxy:
        h.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener(*h)


OP = _opener()


STATUS = {
    200: "ok",
    201: "ok", 202: "ok", 203: "ok", 204: "ok", 206: "ok",
    401: "blocked",   # site refuses non-browser clients; not evidence the offer died
    403: "blocked",
    429: "blocked",
    503: "blocked",
    404: "dead",
    410: "dead",
    0:   "unreachable",
}


def classify(status):
    # Any 2xx means the page answered; Binance's announcement pages reply 202.
    if 200 <= int(status or 0) < 300:
        return "ok"
    return STATUS.get(status, "error")


def check(url, timeout=20):
    """Return (status, final_url). status 0 means transport failure."""
    try:
        req = urllib.request.Request(url, headers=HDRS)
        with OP.open(req, timeout=timeout) as r:
            r.read(2048)
            return r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, (e.geturl() or url)
    except Exception:
        return 0, url


def run(limit=200, only_new=True, delay=0.4):
    c = store.conn()
    where = "WHERE status != 'expired'"
    if only_new:
        where += " AND last_verified IS NULL"
    q = ("SELECT id, official_url FROM deal " + where +
         " ORDER BY score DESC, last_seen DESC LIMIT ?")
    todo = list(c.execute(q, (limit,)))
    ok = bad = 0
    for i, row in enumerate(todo, 1):
        status, final = check(row["official_url"])
        now = int(time.time())
        c.execute("UPDATE deal SET last_verified=?, verify_status=?, verify_kind=?, "
                  "verify_final_url=? WHERE id=?",
                  (now, status, classify(status), final, row["id"]))
        c.execute("INSERT OR REPLACE INTO verify_log(deal_id, at, status, final_url) VALUES(?,?,?,?)",
                  (row["id"], now, status, final))
        kind = classify(status)
        if kind == "ok":
            ok += 1
        else:
            bad += 1
            print("  %-11s %-3d %s" % (kind, status, row["official_url"][:88]))
        c.commit()
        time.sleep(delay)
    c.close()
    print("verified: ok=%d not-ok=%d (of %d)" % (ok, bad, len(todo)))
    return ok, bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--all", action="store_true", help="re-verify already checked links")
    ap.add_argument("--delay", type=float, default=0.4)
    a = ap.parse_args()
    run(limit=a.limit, only_new=not a.all, delay=a.delay)
