import os
import sys
import pandas as pd
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.pipeline.collector import MarketDataCollector, FredDataCollector

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

def ingest_market_data():
    print("Starting Market Data Ingestion...")
    collector = MarketDataCollector()
    # Fetch 1 year of history
    df = collector.fetch_historical_data(period="2y") 
    
    if df.empty:
        print("No market data fetched.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Pre-process: The df has MultiIndex columns if multiple tickers, or simple index if handled in collector
    # In collector.py, I implemented: combined_df = pd.concat(data_frames.values(), axis=1)
    # The columns are just the ticker names (e.g., "Gold", "Silver")
    # Using df.index as Date
    
    records_inserted = 0
    
    for date, row in df.iterrows():
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        
        for symbol in df.columns:
            price = row[symbol]
            if pd.isna(price):
                continue
                
            # SQL Insert for market_data
            sql = """
            INSERT INTO market_data (date, symbol, close_price, volume)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE close_price = VALUES(close_price)
            """
            # Validating types
            # yfinance tickers might be complex objects if not careful, but here they are column names (str)
            
            val = (str(date_str), str(symbol), float(price), int(0))
            
            try:
                cursor.execute(sql, val)
                records_inserted += 1
            except mysql.connector.Error as err:
                print(f"Error inserting {symbol} at {date_str}: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Market Data Ingestion Complete. {records_inserted} records inserted.")

def ingest_fred_data():
    print("Starting Macro Data Ingestion (FRED)...")
    collector = FredDataCollector()
    if not collector.fred:
        print("FRED API Key missing. Skipping.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    records_inserted = 0

    # Fetch logical series history
    # We'll stick to the keys in collector.series_ids
    for name, series_id in collector.series_ids.items():
        try:
            print(f"Fetching {name} ({series_id})...")
            # Get 2 years of data
            series = collector.fred.get_series(series_id, observation_start='2024-01-01')
            
            for date, value in series.items():
                date_str = date.strftime('%Y-%m-%d')
                if pd.isna(value):
                    continue

                sql = """
                INSERT INTO macro_indicators (date, indicator_name, value)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE value = VALUES(value)
                """
                val = (date_str, name, float(value))
                
                try:
                    cursor.execute(sql, val)
                    records_inserted += 1
                except mysql.connector.Error as err:
                    print(f"Error inserting {name} at {date_str}: {err}")
                    
        except Exception as e:
            print(f"Failed to fetch/insert {name}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Macro Data Ingestion Complete. {records_inserted} records inserted.")

if __name__ == "__main__":
    ingest_market_data()
    ingest_fred_data()
