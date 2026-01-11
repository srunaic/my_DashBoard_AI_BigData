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
            st.subheader("📊 Analysis & Alerts")
            
            # 1. Market Regime
            history_df = market_collector.fetch_historical_data(period="6mo")
            if not history_df.empty:
                from analysis.regime import MarketRegimeClassifier
                classifier = MarketRegimeClassifier(history_df)
                regime = classifier.classify_current_regime()
                
                regime_color = "green" if "Risk-On" in regime or "Inflation" in regime else "red"
                st.markdown(f"""
                <div style="margin-bottom: 20px; padding: 15px; border-radius: 8px; background-color: {regime_color}; color: white; text-align: center;">
                    <div style="font-size: 0.8em; opacity: 0.8;">Market Regime</div>
                    <div style="font-size: 1.2em; font-weight: bold;">{regime}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 2. Valuation Alert (Z-Score)
            from analysis.alerts import ValuationAlertSystem
            val_system = ValuationAlertSystem(df_derived)
            status = val_system.check_valuation_status()
            
            if status:
                st.markdown(f"""
                <div style="padding: 15px; border: 2px solid {status['color']}; border-radius: 8px; text-align: center;">
                    <div style="color: {status['color']}; font-weight: bold;">{status['message']}</div>
                    <div style="font-size: 0.8em; margin-top: 5px;">Z-Score: {status['z_score']:.2f} σ</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.info("💡 **Tip**: Buy when Z-Score < -1.0")

                
            st.info("💡 **Tip**: Buy when Z-Score < -1.0")

    else:
        st.warning("No historical derived data found. Please run ingest pipeline.")

    st.markdown("---")
    st.subheader("🔮 AI Price Forecast (30 Days)")
    
    if df_derived is not None and len(df_derived) > 30:
        with st.spinner("Training AI Model (Prophet)..."):
            from analysis.predictor import GoldPredictor
            predictor = GoldPredictor(df_derived)
            
            if predictor.train():
                forecast = predictor.predict(days=30)
                metrics = predictor.get_forecast_metrics()
                
                # Show Metrics
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("30-Day Forecast", f"₩{metrics['future_estimated']:,.0f}")
                with m2:
                    st.metric("Expected Change", f"{metrics['change_pct']:.2f}%", 
                             delta_color="normal" if metrics['trend']=="UP" else "inverse")
                with m3:
                    st.caption("Model: Facebook Prophet")
                    st.caption("Confidence: 95% Interval")

                # Plot Forecast
                # We use Plotly for interactive chart
                # forecast has 'ds', 'yhat', 'yhat_lower', 'yhat_upper'
                
                fig_pred = px.line(forecast, x='ds', y='yhat', title="AI Predicted Trend")
                
                # Add Confidence Interval (Upper/Lower) as filled area?
                # For simplicity in Streamlit standard chart, we might stick to line.
                # Or filter for only future part to highlight it.
                
                # Highlight future
                future_only = forecast[forecast['ds'] > df_derived['date'].max()]
                
                import plotly.graph_objects as go
                fig_go = go.Figure()
                
                # Historical Data
                fig_go.add_trace(go.Scatter(x=df_derived['date'], y=df_derived['value'], mode='lines', name='Actual History'))
                
                # Prediction
                fig_go.add_trace(go.Scatter(x=future_only['ds'], y=future_only['yhat'], mode='lines', name='Predicted (AI)', line=dict(dash='dash', color='purple')))
                
                # Confidence Interval
                fig_go.add_trace(go.Scatter(
                    x=pd.concat([future_only['ds'], future_only['ds'][::-1]]),
                    y=pd.concat([future_only['yhat_upper'], future_only['yhat_lower'][::-1]]),
                    fill='toself',
                    fillcolor='rgba(128, 0, 128, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Confidence Interval'
                ))
                
                fig_go.update_layout(title="Gold Price Scenario (30 Days)", xaxis_title="Date", yaxis_title="Price (KRW)")
                st.plotly_chart(fig_go, use_container_width=True)
                
            else:
                st.error("Not enough data to train AI model (Need > 30 days).")
    else:
        st.info("Insufficient data for AI prediction. Need at least 30 historical data points.")

if __name__ == "__main__":
    main()
