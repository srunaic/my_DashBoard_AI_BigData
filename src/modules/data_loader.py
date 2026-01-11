import pandas as pd
import streamlit as st

class DataLoader:
    def __init__(self, use_db=False, db_connector=None):
        self.use_db = use_db
        self.db_connector = db_connector

    def load_csv(self, file):
        """Loads data from a CSV file uploaded by the user."""
        try:
            df = pd.read_csv(file)
            return df
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return None

    def load_from_db(self, query):
        """Loads data from the database."""
        if self.use_db and self.db_connector:
            return self.db_connector.get_data(query)
        return None
