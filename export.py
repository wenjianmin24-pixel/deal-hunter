# -*- coding: utf-8 -*-
"""Export SQLite -> static site (site/index.html + site/data.js).

The page is fully static: no backend, no API keys, works on GitHub Pages.
Numbers shown are exactly what is in the DB — nothing is estimated in JS.
"""
import json, os, sqlite3, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "hunter.db")
CATS = [
    ("ai", "AI 订阅与工具"), ("crypto", "Crypto 空投与积分"),
    ("card", "U 卡与虚拟卡"), ("bank", "海外银行开户奖励"),
    ("cloud", "VPS 与云服务"), ("software", "软件与数字服务"),
    ("other", "其他全球优惠"),
]
PRICE_LABEL = {
    "free": "完全免费", "trial": "免费试用", "topup": "需充值",
    "deposit": "需存款", "spend": "需消费",
    "volume": "需交易量", "invite": "需邀请", "discount": "折扣/优惠",
    "unknown": "未标注",
}


def rows(c, sql, args=()):
    c.row_factory = sqlite3.Row
    return [dict(r) for r in c.execute(sql, args)]


def build(outdir):
    if not os.path.exists(DB):
        raise SystemExit("hunter.db missing — run collect.py first")
    c = sqlite3.connect(DB)
    now = int(time.time())
    today = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d")

    deals = rows(c, """
        SELECT id,title,category,summary,value,value_usd,region,ends_at,
               official_url,source_name,price_type,risk,score,status,
               first_seen,last_seen,last_verified,verify_status,verify_kind
        FROM deal ORDER BY score DESC, last_seen DESC LIMIT 1200""")

    for d in deals:
        d["price_label"] = PRICE_LABEL.get(d["price_type"], "未标注")
        d["category_label"] = dict(CATS).get(d["category"], d["category"])
        d["first_seen_s"] = datetime.fromtimestamp(d["first_seen"], timezone.utc).strftime("%Y-%m-%d %H:%M")
        d["last_seen_s"] = datetime.fromtimestamp(d["last_seen"], timezone.utc).strftime("%Y-%m-%d %H:%M")
        d["last_verified_s"] = (datetime.fromtimestamp(d["last_verified"], timezone.utc)
                                .strftime("%Y-%m-%d %H:%M")) if d["last_verified"] else ""
        d["is_today"] = 1 if d["first_seen_s"].startswith(today) else 0

    runs = rows(c, "SELECT * FROM run ORDER BY id DESC LIMIT 1")
    last_run = runs[0] if runs else None
    stats = {
        "total": len(deals),
        "active": sum(1 for d in deals if d["status"] != "expired"),
        "expired": sum(1 for d in deals if d["status"] == "expired"),
        "verified": sum(1 for d in deals if d["verify_status"] == 200),
        "blocked": sum(1 for d in deals if d["verify_kind"] == "blocked"),
        "dead": sum(1 for d in deals if d["verify_kind"] == "dead"),
        "deadline": sum(1 for d in deals if d["ends_at"]),
        "sources": len({d["source_name"] for d in deals}),
        "generated": datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "last_run_fetched": (last_run or {}).get("fetched", 0),
    }

    os.makedirs(outdir, exist_ok=True)
    payload = dict(deals=deals, stats=stats, cats=CATS,
                   price_labels=PRICE_LABEL, today=today)
    with open(os.path.join(outdir, "data.js"), "w", encoding="utf-8") as f:
        f.write("window.__DATA__ = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    src = os.path.join(HERE, "index.html")
    with open(src, encoding="utf-8") as f:
        html = f.read()
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("exported %d deals -> %s" % (len(deals), outdir))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "site"))
