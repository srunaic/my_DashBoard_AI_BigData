import yfinance as yf
from fredapi import Fred
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MarketDataCollector:
    def __init__(self):
        self.tickers = {
            "Gold": "GC=F",
            "Silver": "SI=F",
            "USD/KRW": "KRW=X",
            "DXY": "DX-Y.NYB",
            "S&P 500": "^GSPC",
            "KOSPI": "^KS11"
        }

    def fetch_current_prices(self):
        """Fetches the latest available price for all tracked assets."""
        data = {}
        for name, ticker in self.tickers.items():
            try:
                ticker_obj = yf.Ticker(ticker)
                # fast_info is often faster for current price
                price = ticker_obj.fast_info['last_price']
                data[name] = price
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                data[name] = None
        return data

    def fetch_historical_data(self, period="1y"):
        """Fetches historical data for all assets."""
        data_frames = {}
        for name, ticker in self.tickers.items():
            try:
                df = yf.download(ticker, period=period, progress=False)
                # Keep only Close prices for simplicity in this version
                if not df.empty:
                    df = df[['Close']].rename(columns={'Close': name})
                    data_frames[name] = df
            except Exception as e:
                print(f"Error fetching history for {name}: {e}")
        
        # Merge all into one DataFrame
        if data_frames:
            combined_df = pd.concat(data_frames.values(), axis=1)
            return combined_df
        return pd.DataFrame()

class FredDataCollector:
    def __init__(self):
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            print("Warning: FRED_API_KEY not found in environment variables.")
            self.fred = None
        else:
            self.fred = Fred(api_key=api_key)
        
        self.series_ids = {
            "CPI": "CPIAUCSL", # Consumer Price Index for All Urban Consumers
            "M2": "M2SL",      # M2 Money Stock
            "US10Y": "DGS10",  # 10-Year Treasury Constant Maturity Rate
            "FedRate": "FEDFUNDS" # Federal Funds Effective Rate
        }

    def fetch_latest_indicators(self):
        """Fetches the latest value for key macro indicators."""
        data = {}
        if not self.fred:
            return {k: "N/A (No Key)" for k in self.series_ids.keys()}

        for name, series_id in self.series_ids.items():
            try:
                # Get the last observation
                series = self.fred.get_series(series_id, limit=1, sort_order='desc')
                if not series.empty:
                    data[name] = series.iloc[0]
                else:
                    data[name] = None
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                data[name] = None
        return data
