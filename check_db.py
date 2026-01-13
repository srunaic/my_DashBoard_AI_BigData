import sqlite3
import os

db_path = "dashboard.db"
if not os.path.exists(db_path):
    print("DB missing")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT count(*) FROM macro_raw")
        print(f"macro_raw: {c.fetchone()[0]}")
        
        c.execute("SELECT count(*) FROM domestic_market_raw")
        print(f"domestic_market_raw: {c.fetchone()[0]}")
        
        c.execute("SELECT count(*) FROM market_premium_derived")
        print(f"market_premium_derived: {c.fetchone()[0]}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
