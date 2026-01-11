import streamlit as st
import sys
import os

# Add the src directory to the python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.db_connector import DBConnector

def main():
    st.set_page_config(
        page_title="AI Big Data Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 AI & Big Data Analysis Dashboard")

    # Sidebar for Configuration
    with st.sidebar:
        st.header("Settings")
        st.subheader("Database Connection")
        db_host = st.text_input("Host", "localhost")
        db_user = st.text_input("User", "root")
        db_password = st.text_input("Password", type="password")
        db_name = st.text_input("Database Name", "test") # Default to 'test' or generic
        
        if st.button("Connect"):
            connector = DBConnector(host=db_host, user=db_user, password=db_password, database=db_name)
            if connector.connect():
                st.success("Connected successfully!")
            else:
                st.error("Failed to connect.")

    # Main Content Area
    st.write("Welcome to the dashboard. Select a module from the sidebar or configure your database connection.")

    # Placeholder for future metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "Active")
    col2.metric("Data Source", "Local MySQL")
    col3.metric("System", "Ready")

if __name__ == "__main__":
    main()
