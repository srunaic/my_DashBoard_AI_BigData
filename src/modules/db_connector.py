import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

class DBConnector:
    def __init__(self, host="localhost", user="root", password="", port=3306, database=None):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = database
        self.engine = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            # Construct the connection string
            # If database is not specified, we connect to the server only (useful for initial checks)
            db_str = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}"
            if self.database:
                db_str += f"/{self.database}"
            
            self.engine = create_engine(db_str)
            # Test connection
            with self.engine.connect() as connection:
                pass
            return True
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return False

    def get_data(self, query):
        """Executes a SQL query and returns a Pandas DataFrame."""
        if not self.engine:
            if not self.connect():
                return None
        
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            st.error(f"Query execution failed: {e}")
            return None

    def execute_query(self, query):
        """Executes a SQL command (INSERT, UPDATE, DELETE)."""
        if not self.engine:
            if not self.connect():
                return None
            
        try:
            with self.engine.connect() as connection:
                connection.execute(query)
            return True
        except Exception as e:
            st.error(f"Execution failed: {e}")
            return False
