import streamlit as st
import sys
import os

# Add the src directory to the python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.db_connector import DBConnector
from pipeline.collector import MarketDataCollector, FredDataCollector
from ui.dashboard import render_dashboard

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

    # Main Content
    st.write("### 📊 Market Overview")
    
    # 1. Fetch Data
    market_collector = MarketDataCollector()
    current_prices = market_collector.fetch_current_prices()
    
    # 2. Display KPI Cards
    if current_prices:
        cols = st.columns(len(current_prices))
        for idx, (name, price) in enumerate(current_prices.items()):
            with cols[idx]:
                st.metric(label=name, value=f"{price:,.2f}" if price else "N/A")

    # 3. Fetch Historical Data for Charts
    history_df = market_collector.fetch_historical_data()
    
    # 4. Analysis & Insights
    if not history_df.empty:
        # Calculate Signals (Regime)
        from analysis.regime import MarketRegimeClassifier
        regime_classifier = MarketRegimeClassifier(history_df)
        current_regime = regime_classifier.classify_current_regime()
        
        st.markdown(f"## 🚦 Market Regime: **{current_regime}**")
        st.info("Regime is calculated based on Price Trends (Gold, SPX) and Currency Strength (DXY).")
        
        render_dashboard(history_df)

    st.write("---")
    st.write("### 🏦 Macro Indicators (FRED)")
    
    fred_collector = FredDataCollector()
    indicators = fred_collector.fetch_latest_indicators()
    
    if indicators:
        i_cols = st.columns(len(indicators))
        for idx, (name, val) in enumerate(indicators.items()):
            with i_cols[idx]:
                st.metric(label=name, value=f"{val:,.2f}" if val else "N/A")

if __name__ == "__main__":
    main()
