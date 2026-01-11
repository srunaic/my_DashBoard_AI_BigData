import streamlit as st
import plotly.express as px
import pandas as pd

def render_dashboard(data=None):
    """Renders the main dashboard charts."""
    st.header("📈 Data Overview")
    
    if data is None or data.empty:
        st.info("No data available to display. Please connect to a database or load a CSV.")
        
        # Example dummy chart for visualization purposes
        st.markdown("### Example Visualization")
        df = pd.DataFrame({
            "Category": ["A", "B", "C", "D"],
            "Values": [10, 20, 15, 25]
        })
        fig = px.bar(df, x="Category", y="Values", title="Sample Chart")
        st.plotly_chart(fig, use_container_width=True)
        return

    # If data is provided, try to render generic charts
    st.write(f"Loaded {len(data)} rows of market data.")
    
    # Line Chart for all assets (Normalized or Separate?)
    # For now, just a raw line chart
    st.subheader("Price History (1 Year)")
    st.line_chart(data)
    
    # Correlation Heatmap
    if len(data.columns) > 1:
        st.subheader("Correlation Heatmap")
        corr = data.corr()
        fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
        st.plotly_chart(fig, use_container_width=True)
