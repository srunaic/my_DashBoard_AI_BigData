import os
import sys
import pandas as pd
import mysql.connector
import sqlite3
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.modules.converter import get_gold_don_price_krw

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "dashboard_db")
# Handle cases where DB_PORT is an empty string
env_port = os.getenv("DB_PORT")
DB_PORT = int(env_port) if env_port and env_port.strip() else 3306

def get_db_connection():
    from src.modules.db_connector import DBConnector
    connector = DBConnector()
    return connector.get_connection()

def run_derivation():
    print("Starting Metric Derivation (Raw -> Derived)...")
    conn = get_db_connection()
    
    # 1. Load Raw Data (Gold USD and USD/KRW)
    # Pivot logic: We need dates where we have BOTH Gold and Exchange Rate
    query = """
    SELECT date, symbol, value 
    FROM macro_raw 
    WHERE symbol IN ('GOLD_USD_OZ', 'USDKRW')
    """
    
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print("No raw data found to derive metrics from.")
        conn.close()
        return

    # Pivot to have columns: date, GOLD_USD_OZ, USDKRW
    df_pivot = df.pivot(index='date', columns='symbol', values='value').dropna()
    
    # Ensure index is datetime (SQLite returns str)
    df_pivot.index = pd.to_datetime(df_pivot.index)
    
    derived_count = 0
    cursor = conn.cursor()
    
    is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in sys.modules else False
    
    for date, row in df_pivot.iterrows():
        gold_oz = row.get('GOLD_USD_OZ')
        usdkrw = row.get('USDKRW')
        
        # Calculate Gold 1 Don (KRW)
        gold_don_krw = get_gold_don_price_krw(gold_oz, usdkrw)
        
        if gold_don_krw:
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            metric_name = "GOLD_KRW_DON"
            
            if is_sqlite:
                sql = """
                INSERT OR REPLACE INTO macro_derived (date, metric, value, calculation_version)
                VALUES (?, ?, ?, ?)
                """
                val = (str(date_str), metric_name, float(gold_don_krw), "v1.0")
            else:
                sql = """
                INSERT INTO macro_derived (date, metric, value, calculation_version)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE value = VALUES(value)
                """
                val = (date_str, metric_name, float(gold_don_krw), "v1.0")
            
            try:
                cursor.execute(sql, val)
                derived_count += 1
            except mysql.connector.Error as err:
                print(f"Error inserting derived metric at {date_str}: {err}")
            except sqlite3.Error as err:
                print(f"Error inserting derived metric at {date_str}: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Derivation Complete. {derived_count} metrics (Gold Don KRW) calculated and stored.")

def run_premium_derivation():
    print("Starting Premium Analysis (Theoretical vs Domestic)...")
    # Import inside function or ensure path is present
    from src.analysis.premium import PremiumCalculator
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Join macro_derived (Theoretical) and domestic_market_raw (Physical)
    # matching on Date (roughly). Since domestic might be daily and derived might be daily, we join on DATE(date).
    # Note: timestamp mismatch handling requires Date casting.
    
    query = """
    SELECT 
        DATE(t1.date) as date,
        t1.value as theoretical,
        t2.value as physical
    FROM macro_derived t1
    JOIN domestic_market_raw t2 ON DATE(t1.date) = DATE(t2.date)
    WHERE t1.metric = 'GOLD_KRW_DON' AND t2.price_type = 'BUYing'
    """
    
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print("No matching data found for Premium Calculation.")
        # Setup mock derived data if missing, for the sake of the demo flow, 
        # or simply return.
        pass

    calculator = PremiumCalculator()
    inserted_count = 0
    is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in sys.modules else False
    
    for _, row in df.iterrows():
        theo = row['theoretical']
        phys = row['physical']
        date_str = str(row['date'])
        
        result = calculator.calculate_premium(phys, theo)
        
        if result:
            if is_sqlite:
                sql = """
                INSERT OR REPLACE INTO market_premium_derived 
                (date, theoretical_price, physical_price, premium_amount, premium_rate)
                VALUES (?, ?, ?, ?, ?)
                """
                val = (date_str, float(theo), float(phys), float(result['amount']), float(result['rate']))
            else:
                sql = """
                INSERT INTO market_premium_derived 
                (date, theoretical_price, physical_price, premium_amount, premium_rate)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE premium_rate = VALUES(premium_rate)
                """
                val = (date_str, float(theo), float(phys), float(result['amount']), float(result['rate']))
            
            try:
                cursor.execute(sql, val)
                inserted_count += 1
            except mysql.connector.Error as err:
                print(f"Error inserting premium for {date_str}: {err}")
            except sqlite3.Error as err:
                print(f"Error inserting premium for {date_str}: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Premium Derivation Complete. {inserted_count} records analysed.")

if __name__ == "__main__":
    run_derivation()
    run_premium_derivation()
