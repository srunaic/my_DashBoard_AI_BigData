import pandas as pd

class MarketRegimeClassifier:
    def __init__(self, data_df):
        """
        data_df: Combined DataFrame containing Gold, DXY, US10Y (Yield), S&P 500 etc.
        """
        self.df = data_df

    def classify_current_regime(self):
        """
        Determines the current market regime based on basic rules.
        Returns: strict string label (Risk-On, Risk-Off, Inflation-Hedge, Unclear)
        """
        # Get latest slice (last 5 days average to smooth noise)
        recent = self.df.tail(5).mean()
        
        # Needed Columns check
        required = ['Gold', 'DXY', 'S&P 500']
        for col in required:
            if col not in self.df.columns:
                return "Insufficient Data"

        # Calculate Trends (Prices vs 50-day Moving Average of the last available day)
        # Note: self.df should contain computed MAs or we compute them here
        ma_50 = self.df.rolling(window=50).mean().iloc[-1]
        current = self.df.iloc[-1]

        gold_trend = "UP" if current['Gold'] > ma_50['Gold'] else "DOWN"
        dxy_trend = "UP" if current['DXY'] > ma_50['DXY'] else "DOWN"
        spx_trend = "UP" if current['S&P 500'] > ma_50['S&P 500'] else "DOWN"
        
        # Rule Engine Logic
        # 1. Risk-On: Stocks UP, DXY DOWN (usually), Gold (Variable, but usually stable/variable)
        if spx_trend == "UP" and dxy_trend == "DOWN":
            return "Risk-On (Growth)"
            
        # 2. Risk-Off / Fear: Stocks DOWN, DXY UP, Gold UP (Safe Haven)
        elif spx_trend == "DOWN" and current['Gold'] > ma_50['Gold']:
            return "Risk-Off (Fear)"
            
        # 3. Inflation Hedge: Gold UP strongly, DXY DOWN or Weak
        elif gold_trend == "UP" and dxy_trend == "DOWN":
            return "Inflation Hedge"
            
        # 4. Strong Dollar Pressure: DXY UP, Gold DOWN, Stocks DOWN
        elif dxy_trend == "UP" and gold_trend == "DOWN" and spx_trend == "DOWN":
            return "Deflation/Cash is King"

        return "Mixed/Transition"

    def detect_signals(self):
        """
        Scans history to generate a log of regime changes.
        """
        # Simplistic implementation: Apply logic to the whole dataframe row by row
        # (Optimization: vectorize this in future)
        signals = []
        ma_50 = self.df.rolling(window=50).mean()
        
        for date, row in self.df.iterrows():
            if date not in ma_50.index or pd.isna(ma_50.loc[date, 'Gold']):
                continue
                
            cur_ma = ma_50.loc[date]
            
            # Logic duplication (ideally refactor to single function taking row & ma)
            gold_up = row['Gold'] > cur_ma['Gold']
            spx_up = row['S&P 500'] > cur_ma['S&P 500']
            dxy_up = row['DXY'] > cur_ma['DXY']
            
            regime = "Neutral"
            if spx_up and not dxy_up:
                regime = "Risk-On"
            elif not spx_up and gold_up:
                regime = "Risk-Off"
            elif gold_up and not dxy_up:
                regime = "Inflation Hedge"
            elif dxy_up and not gold_up and not spx_up:
                regime = "Deflation"
                
            signals.append({'date': date, 'regime': regime})
            
        return pd.DataFrame(signals).set_index('date')
