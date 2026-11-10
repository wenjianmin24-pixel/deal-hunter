import sqlite3, os
db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hunter.db")
c = sqlite3.connect(db); c.row_factory = sqlite3.Row
q = lambda s: c.execute(s).fetchall()
print("total", q("select count(*) from deal")[0][0])
print("--- category ---")
for r in q("select category,count(*) n from deal group by 1 order by n desc"):
    print("  %-10s %d" % (r["category"], r["n"]))
print("--- price_type ---")
for r in q("select price_type,count(*) n from deal group by 1 order by n desc"):
    print("  %-10s %d" % (r["price_type"], r["n"]))
print("deadlines", q("select count(*) from deal where ends_at is not null")[0][0],
      "| values", q("select count(*) from deal where value_usd is not null")[0][0],
      "| regions", q('select count(*) from deal where region != \'\'')[0][0])
print()
print("=== TOP 15 by score ===")
for r in q("select score,price_type,category,value,ends_at,region,title,source_name from deal order by score desc limit 15"):
    print("%6.1f %-7s %-9s %-9s %-10s %-14s [%s] %s" % (
        r["score"], r["price_type"], r["category"], (r["value"] or "")[:9],
        (r["ends_at"] or "")[:10], (r["region"] or "")[:14], r["source_name"][:14], r["title"][:70]))
print()
print("=== deadlines ===")
for r in q("select ends_at,title from deal where ends_at is not null order by ends_at limit 12"):
    print("  %s  %s" % (r["ends_at"], r["title"][:78]))
print()
print("=== free / trial ===")
for r in q("select price_type,value,title,source_name from deal where price_type in ('free','trial') limit 12"):
    print("  %-6s %-8s [%s] %s" % (r["price_type"], (r["value"] or "")[:8], r["source_name"][:14], r["title"][:70]))
