import mysql.connector
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class DBConnector:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.host = host or os.getenv("DB_HOST", "localhost")
        self.user = user or os.getenv("DB_USER", "root")
        self.password = password or os.getenv("DB_PASSWORD", "")
        self.database = database or os.getenv("DB_NAME", "dashboard_db")
        self.port = int(os.getenv("DB_PORT", 3306))
        
        # Determine connection mode
        self.use_sqlite = False
        # Path for the SQLite DB file (in the project root)
        self.sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dashboard.db"))

    def get_connection(self):
        """
        Returns a raw database connection.
        Prioritizes MySQL. Falls back to SQLite if MySQL fails.
        """
        # 1. Try MySQL First
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=3
            )
            return conn
        except Exception as e:
            # 2. Fallback to SQLite
            print(f"⚠️ MySQL Connection Failed: {e}")
            print(f"🔄 Falling back to SQLite: {self.sqlite_path}")
            self.use_sqlite = True
            return sqlite3.connect(self.sqlite_path)

    def get_data(self, query):
        """
        Executes a SELECT query and returns a Pandas DataFrame.
        """
        conn = self.get_connection()
        try:
            return pd.read_sql(query, conn)
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if conn:
                conn.close()
