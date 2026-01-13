import os
import sys
import pandas as pd
import mysql.connector
import sqlite3
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
# Handle cases where DB_PORT is an empty string
env_port = os.getenv("DB_PORT")
DB_PORT = int(env_port) if env_port and env_port.strip() else 3306

def get_db_connection():
    # Use the unified DBConnector to handle fallback
    from src.modules.db_connector import DBConnector
    connector = DBConnector()
    return connector.get_connection()

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
            
            # Map symbol to standard Raw Symbol Names
            # yfinance names: "Gold", "Silver", "USD/KRW", etc. (from collector keys)
            raw_symbol_map = {
                "Gold": "GOLD_USD_OZ",
                "Silver": "SILVER_USD_OZ",
                "USD/KRW": "USDKRW",
                "DXY": "DXY_INDEX",
                "S&P 500": "SPX_INDEX",
                "KOSPI": "KOSPI_INDEX"
            }
            db_symbol = raw_symbol_map.get(str(symbol), str(symbol))
            
            # Determine Unit
            unit = "INDEX"
            if "USD" in db_symbol: unit = "USD"
            if "KRW" in db_symbol: unit = "KRW"
            if "OZ" in db_symbol: unit = "USD/oz"
            
            # SQL Insert for macro_raw
            # SQL Insert for macro_raw
            # Detect DB Type
            is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in sys.modules else False
            
            if is_sqlite:
                sql = """
                INSERT OR REPLACE INTO macro_raw (date, symbol, value, unit, source)
                VALUES (?, ?, ?, ?, ?)
                """
                val = (str(date_str), str(db_symbol), float(price), str(unit), "yfinance")
                # SQLite uses ? placeholder
            else:
                sql = """
                INSERT INTO macro_raw (date, symbol, value, unit, source)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE value = VALUES(value)
                """
                val = (str(date_str), str(db_symbol), float(price), str(unit), "yfinance")
            
            try:
                cursor.execute(sql, val)
                records_inserted += 1
            except mysql.connector.Error as err:
                print(f"Error inserting {db_symbol} at {date_str}: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Market Data Ingestion Complete. {records_inserted} records inserted into macro_raw.")

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
    for name, series_id in collector.series_ids.items():
        try:
            print(f"Fetching {name} ({series_id})...")
            # Get 2 years of data
            series = collector.fred.get_series(series_id, observation_start='2024-01-01')
            
            for date, value in series.items():
                date_str = date.strftime('%Y-%m-%d')
                if pd.isna(value):
                    continue

                # Standardize Names
                db_symbol_map = {
                    "CPI": "CPI_INDEX",
                    "M2": "M2_SUPPLY",
                    "US10Y": "US10Y_YIELD",
                    "FedRate": "FED_RATE"
                }
                db_symbol = db_symbol_map.get(name, name)
                
                unit = "INDEX"
                if "RATE" in db_symbol or "YIELD" in db_symbol: unit = "%"
                if "M2" in db_symbol: unit = "USD_BILLIONS"

                # SQL Insert
                # Detect DB Type
                is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in sys.modules else False
                
                if is_sqlite:
                    sql = """
                    INSERT OR REPLACE INTO macro_raw (date, symbol, value, unit, source)
                    VALUES (?, ?, ?, ?, ?)
                    """
                    val = (str(date_str), str(db_symbol), float(value), str(unit), "FRED")
                else:
                    sql = """
                    INSERT INTO macro_raw (date, symbol, value, unit, source)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE value = VALUES(value)
                    """
                    val = (date_str, db_symbol, float(value), unit, "FRED")
                
                try:
                    cursor.execute(sql, val)
                    records_inserted += 1
                except mysql.connector.Error as err:
                    print(f"Error inserting {db_symbol} at {date_str}: {err}")
                except sqlite3.Error as err:
                    print(f"Error inserting {db_symbol} at {date_str}: {err}")
                    
        except Exception as e:
            print(f"Failed to fetch/insert {name}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Macro Data Ingestion Complete. {records_inserted} records inserted into macro_raw.")

def ingest_domestic_data():
    print("Starting Domestic Gold Data Ingestion...")
    from src.modules.domestic_collector import DomesticGoldCollector
    
    collector = DomesticGoldCollector()
    # Using Mock for now as agreed
    data = collector.fetch_latest_mock()
    
    if data:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL Insert
        is_sqlite = isinstance(conn, sqlite3.Connection) if 'sqlite3' in sys.modules else False
        
        if is_sqlite:
            sql = """
            INSERT OR REPLACE INTO domestic_market_raw (date, price_type, value, unit, source)
            VALUES (?, ?, ?, ?, ?)
            """
            val = (str(data['date']), str(data['type']), float(data['value']), str(data['unit']), "MOCK_TEST")
        else:
            sql = """
            INSERT INTO domestic_market_raw (date, price_type, value, unit, source)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE value = VALUES(value)
            """
            val = (data['date'], data['type'], data['value'], data['unit'], "MOCK_TEST")
        
        try:
            cursor.execute(sql, val)
            conn.commit()
            print(f"Domestic Data Ingested: {data['value']} KRW ({data['date']})")
        except mysql.connector.Error as err:
            print(f"Error inserting domestic data: {err}")
        except sqlite3.Error as err:
            print(f"Error inserting domestic data: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("No domestic data fetched.")

if __name__ == "__main__":
    ingest_market_data()
    ingest_fred_data()
    ingest_domestic_data()
