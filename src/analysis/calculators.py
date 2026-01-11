import pandas as pd
import numpy as np

class MetricCalculator:
    def __init__(self, market_df, macro_df):
        """
        market_df: DataFrame with datetime index and columns like ['Gold', 'Silver', 'DXY', 'USD/KRW']
        macro_df: DataFrame with 'indicator_name' and 'value'. Needs processing to align with market_df.
        """
        self.market_df = market_df
        self.macro_df = macro_df

    def calculate_real_gold_price(self):
        """
        Calculates Real Gold Price = Nominal Gold Price / CPI * (Base CPI)
        """
        if 'Gold' not in self.market_df.columns:
            return None

        # Process CPI from macro_df
        # macro_df expects: date, indicator_name, value
        cpi_df = self.macro_df[self.macro_df['indicator_name'] == 'CPI'].copy()
        if cpi_df.empty:
            return self.market_df['Gold'] # Return nominal if no CPI

        cpi_df['date'] = pd.to_datetime(cpi_df['date'])
        cpi_df = cpi_df.set_index('date').sort_index()
        
        # Resample CPI to daily to match market data (forward fill)
        # We need to ensure the index covers the market data range
        cpi_daily = cpi_df['value'].reindex(self.market_df.index, method='ffill')

        # Base CPI (e.g., the last available CPI or a specific year). Let's use the most recent for "current real value"
        base_cpi = cpi_daily.iloc[-1]
        
        # Real Price = Price / CPI * Base_CPI
        real_price = self.market_df['Gold'] / cpi_daily * base_cpi
        return real_price

    def calculate_rolling_correlations(self, asset1, asset2, window=30):
        """
        Calculates rolling correlation between two assets.
        """
        if asset1 not in self.market_df.columns or asset2 not in self.market_df.columns:
            return None
        
        return self.market_df[asset1].rolling(window=window).corr(self.market_df[asset2])

    def calculate_volatility(self, window=30):
        """
        Calculates annualized volatility for all assets.
        """
        returns = self.market_df.pct_change()
        volatility = returns.rolling(window=window).std() * np.sqrt(252) # Annualized
        return volatility
