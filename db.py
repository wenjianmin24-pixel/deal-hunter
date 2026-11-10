# -*- coding: utf-8 -*-
import os, sqlite3, time

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hunter.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS deal(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fp TEXT UNIQUE,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  summary TEXT,
  value TEXT,
  value_usd REAL,
  requirements TEXT,
  region TEXT,
  starts_at TEXT,
  ends_at TEXT,
  steps TEXT,
  official_url TEXT,
  source_name TEXT,
  source_url TEXT,
  price_type TEXT,
  risk TEXT,
  score REAL,
  status TEXT,
  first_seen INTEGER,
  last_seen INTEGER,
  last_verified INTEGER,
  verify_status INTEGER,
  verify_kind TEXT,
  verify_final_url TEXT
);
CREATE INDEX IF NOT EXISTS idx_deal_cat ON deal(category);
CREATE INDEX IF NOT EXISTS idx_deal_status ON deal(status);
CREATE INDEX IF NOT EXISTS idx_deal_lastseen ON deal(last_seen);
CREATE TABLE IF NOT EXISTS run(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started INTEGER, finished INTEGER,
  fetched INTEGER DEFAULT 0, inserted INTEGER DEFAULT 0,
  updated INTEGER DEFAULT 0, errors TEXT
);
CREATE TABLE IF NOT EXISTS verify_log(
  deal_id INTEGER, at INTEGER, status INTEGER, final_url TEXT,
  PRIMARY KEY(deal_id, at)
);
"""

MIGRATIONS = [
    ("deal", "verify_kind", "TEXT"),
]


def conn():
    c = sqlite3.connect(DB, timeout=30)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    # CREATE TABLE IF NOT EXISTS never adds a column to an existing db
    for table, col, decl in MIGRATIONS:
        cols = {r[1] for r in c.execute("PRAGMA table_info(%s)" % table)}
        if col not in cols:
            c.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table, col, decl))
            c.commit()
    return c

def upsert_deal(c, d, now=None):
    now = now or int(time.time())
    row = c.execute("SELECT id FROM deal WHERE fp=?", (d["fp"],)).fetchone()
    if row:
        c.execute("""UPDATE deal SET last_seen=?, title=?, summary=?, category=?,
                     value=?, value_usd=?, price_type=?, score=?,
                     ends_at=COALESCE(ends_at, ?), official_url=COALESCE(official_url, ?)
                     WHERE id=?""",
                  (now, d["title"], d.get("summary"), d["category"], d.get("value"),
                   d.get("value_usd"), d.get("price_type"), d.get("score"),
                   d.get("ends_at"), d.get("official_url"), row["id"]))
        return "update"
    c.execute("""INSERT INTO deal(fp,title,category,summary,value,value_usd,requirements,
                 region,starts_at,ends_at,steps,official_url,source_name,source_url,
                 price_type,risk,score,status,first_seen,last_seen)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (d["fp"], d["title"], d["category"], d.get("summary"), d.get("value"),
               d.get("value_usd"), d.get("requirements"), d.get("region"),
               d.get("starts_at"), d.get("ends_at"), d.get("steps"),
               d.get("official_url"), d.get("source_name"), d.get("source_url"),
               d.get("price_type"), d.get("risk"), d.get("score"), "active", now, now))
    return "insert"

def expire(c, now=None):
    now = now or int(time.time())
    today = time.strftime("%Y-%m-%d", time.gmtime(now))
    return c.execute("""UPDATE deal SET status='expired'
                        WHERE ends_at IS NOT NULL AND ends_at != '' AND ends_at < ?
                          AND status != 'expired'""", (today,)).rowcount
