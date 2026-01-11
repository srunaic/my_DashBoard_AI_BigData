import plotly.express as px
import plotly.graph_objects as go

def plot_line_chart(df, x_col, y_col, title="Time Series"):
    """Creates a simple line chart."""
    fig = px.line(df, x=x_col, y=y_col, title=title)
    return fig

def plot_bar_chart(df, x_col, y_col, title="Bar Chart"):
    """Creates a simple bar chart."""
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    return fig

def plot_correlation_heatmap(corr_matrix):
    """Creates a heatmap for correlation matrix."""
    fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Heatmap")
    return fig
