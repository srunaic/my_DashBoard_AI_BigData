import streamlit as st
import sys
import os

# Add the src directory to the python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from modules.db_connector import DBConnector
from pipeline.collector import MarketDataCollector, FredDataCollector
from ui.dashboard import render_dashboard

from modules.converter import get_gold_don_price_krw
import pandas as pd
import plotly.express as px

def main():
    st.set_page_config(
        page_title="Gold & Macro Decision System",
        page_icon="🏦",
        layout="wide"
    )

    st.title("🏦 Enterprise Macro Analysis System")
    st.markdown("### 🥇 Standard: Gold 1 Don (3.75g)")

    # 1. Fetch Live Data for KPIs
    market_collector = MarketDataCollector()
    current_prices = market_collector.fetch_current_prices() 
    # current_prices keys: "Gold" (USD/oz), "Silver", "USD/KRW", etc.
    
    if current_prices:
        # Calculate Derived KPIs
        gold_oz_usd = current_prices.get("Gold")
        usd_krw = current_prices.get("USD/KRW")
        
        gold_don_krw = get_gold_don_price_krw(gold_oz_usd, usd_krw)
        
        # Layout
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.metric("Gold (1 Don/KRW)", f"₩{gold_don_krw:,.0f}" if gold_don_krw else "N/A", help="3.75g Standard")
        with kpi2:
            st.metric("Gold (Intl/USD)", f"${gold_oz_usd:,.2f}" if gold_oz_usd else "N/A", "per oz")
        with kpi3:
            st.metric("USD/KRW", f"₩{usd_krw:,.2f}" if usd_krw else "N/A")
        with kpi4:
            dxy = current_prices.get("DXY")
            st.metric("Dollar Index (DXY)", f"{dxy:,.2f}" if dxy else "N/A")

    st.markdown("---")
    
    # 2. Historical Analysis (From DB)
    # We want to show the Trend of Gold 1 Don (Derived)
    connector = DBConnector(host="localhost", user="root", password="", database="dashboard_db")
    
    # Fetch Derived Data
    query_derived = "SELECT date, value FROM macro_derived WHERE metric='GOLD_KRW_DON' ORDER BY date ASC"
    df_derived = connector.get_data(query_derived)
    
    if df_derived is not None and not df_derived.empty:
        df_derived['date'] = pd.to_datetime(df_derived['date'])
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("📈 Gold Price Trend (KRW / 1 Don)")
            fig = px.line(df_derived, x='date', y='value', title="Gold 1 Don Price (KRW)")
            fig.update_layout(xaxis_title="Date", yaxis_title="Price (KRW)")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_side:
            st.subheader("📊 Market Regime")
            # Fetch Raw History for Regime Calc
            # For simplicity, we can reuse the collector's history or fetch from DB.
            # Let's fetch from DB for consistency if we had a full ingestion. 
            # But the collector history is easier for the existing Class.
            
            # Re-using collector for now to get the multi-asset dataframe for regime
            history_df = market_collector.fetch_historical_data(period="6mo")
            
            if not history_df.empty:
                from analysis.regime import MarketRegimeClassifier
                classifier = MarketRegimeClassifier(history_df)
                regime = classifier.classify_current_regime()
                
                # Dynamic Color
                color = "green" if "Risk-On" in regime or "Inflation" in regime else "red"
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; background-color: {color}; color: white; text-align: center;">
                    <h2>{regime}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                **Strategy Guide:**
                - **Risk-On**: Focus on Equities.
                - **Risk-Off**: Hold Gold/Cash.
                - **Inflation Hedge**: Accumulate Gold.
                """)

    else:
        st.warning("No historical derived data found. Please run ingest pipeline.")

if __name__ == "__main__":
    main()
