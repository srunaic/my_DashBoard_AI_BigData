from prophet import Prophet
import pandas as pd

class GoldPredictor:
    def __init__(self, history_df):
        """
        history_df: DataFrame containing 'date' and 'value' (Gold 1 Don KRW)
        """
        self.df = history_df.rename(columns={'date': 'ds', 'value': 'y'})
        self.model = None
        self.forecast = None

    def train(self):
        """
        Trains the Prophet model.
        """
        if len(self.df) < 30:
            return False # Not enough data
            
        self.model = Prophet(
            daily_seasonality=True,
            yearly_seasonality=True,
            weekly_seasonality=False,
            changepoint_prior_scale=0.05
        )
        self.model.fit(self.df)
        return True

    def predict(self, days=30):
        """
        Generates forecast for the next 'days'.
        """
        if self.model is None:
            return None
            
        future = self.model.make_future_dataframe(periods=days)
        self.forecast = self.model.predict(future)
        return self.forecast

    def get_forecast_metrics(self):
        """
        Returns the expected price in 30 days and the trend.
        """
        if self.forecast is None:
            return None
            
        current = self.forecast.iloc[-31]['yhat'] # roughly today (before 30 days future)
        future = self.forecast.iloc[-1]['yhat']
        
        change_pct = ((future - current) / current) * 100
        
        return {
            "current_estimated": current,
            "future_estimated": future,
            "change_pct": change_pct,
            "trend": "UP" if change_pct > 0 else "DOWN"
        }
