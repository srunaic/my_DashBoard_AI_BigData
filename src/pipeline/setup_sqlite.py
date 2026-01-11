import sqlite3
import os
import sys

# Add src path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def init_sqlite_db():
    db_path = os.path.join(os.path.dirname(__file__), '../../dashboard.db')
    
    # Remove existing to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating SQLite DB at {db_path}...")
    
    # Create Tables (Simplified DDL for SQLite)
    
    # 1. Macro Raw
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS macro_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        symbol TEXT,
        value REAL,
        unit TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, symbol)
    );
    """)
    
    # 2. Macro Derived
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS macro_derived (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        metric TEXT,
        value REAL,
        calculation_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, metric)
    );
    """)
    
    # 3. Domestic Market Raw (Updated for Phase 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domestic_market_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        price_type TEXT,
        value REAL,
        unit TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, price_type)
    );
    """)

    # 4. Market Premium Derived (Updated for Phase 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_premium_derived (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        theoretical_price REAL,
        physical_price REAL,
        premium_amount REAL,
        premium_rate REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date)
    );
    """)
    
    conn.commit()
    conn.close()
    print("SQLite Initialized.")

if __name__ == "__main__":
    init_sqlite_db()
