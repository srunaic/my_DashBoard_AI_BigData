import os
import sys
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.modules.converter import get_gold_don_price_krw

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "dashboard_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

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
    
    derived_count = 0
    cursor = conn.cursor()
    
    for date, row in df_pivot.iterrows():
        gold_oz = row.get('GOLD_USD_OZ')
        usdkrw = row.get('USDKRW')
        
        # Calculate Gold 1 Don (KRW)
        gold_don_krw = get_gold_don_price_krw(gold_oz, usdkrw)
        
        if gold_don_krw:
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            metric_name = "GOLD_KRW_DON"
            
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

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Derivation Complete. {derived_count} metrics (Gold Don KRW) calculated and stored.")

if __name__ == "__main__":
    run_derivation()
