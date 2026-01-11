import pandas as pd
import numpy as np

class ValuationAlertSystem:
    def __init__(self, history_df):
        """
        history_df: DataFrame with 'date' and 'value' (Gold 1 Don KRW)
        """
        self.df = history_df.sort_values('date')

    def check_valuation_status(self, window=365*3): # Default 3 years
        """
        Checks if the current price is statistically overvalued or undervalued
        based on a rolling Z-Score (Standard Deviations from Mean).
        
        Using a shorter window (e.g., 180 days) if 3 years data is not available.
        """
        if len(self.df) < 30:
            return None # Not enough data

        # Adjust window to available data
        effective_window = min(window, len(self.df))
        
        # Calculate Rolling Stats
        self.df['MA'] = self.df['value'].rolling(window=effective_window).mean()
        self.df['STD'] = self.df['value'].rolling(window=effective_window).std()
        self.df['Z_Score'] = (self.df['value'] - self.df['MA']) / self.df['STD']
        
        current = self.df.iloc[-1]
        z_score = current['Z_Score']
        
        status = {
            "z_score": z_score,
            "level": "Neutral",
            "message": "Fairly Valued",
            "color": "gray"
        }
        
        if z_score > 2.0:
            status["level"] = "Critical High"
            status["message"] = "⚠️ Extreme Overvaluation (Sell Signal)"
            status["color"] = "red"
        elif z_score > 1.0:
            status["level"] = "High"
            status["message"] = "Overvalued (Caution)"
            status["color"] = "orange"
        elif z_score < -2.0:
            status["level"] = "Critical Low"
            status["message"] = "💎 Extreme Undervaluation (Strong Buy)"
            status["color"] = "green"
        elif z_score < -1.0:
            status["level"] = "Low"
            status["message"] = "Undervalued (Accumulate)"
            status["color"] = "lightgreen"
            
        return status

    def check_driver_analysis(self, gold_usd_change, usdkrw_change):
        """
        Determines what is driving the local price change.
        Input: Percentage change (float) over a period (e.g. 1 month).
        """
        # Logic: If FX move is dominant > Gold move
        if abs(usdkrw_change) > abs(gold_usd_change) * 1.5:
            return "Currency Driven (USD/KRW Volatility)"
        elif abs(gold_usd_change) > abs(usdkrw_change) * 1.5:
            return "Commodity Driven (Global Gold Price)"
        else:
            return "Composite (Both Factors)"
