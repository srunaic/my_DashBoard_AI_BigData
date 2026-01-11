import pandas as pd
import numpy as np

class Analyzer:
    def __init__(self, data):
        self.data = data

    def get_basic_stats(self):
        """Returns basic descriptive statistics."""
        if self.data is not None:
            return self.data.describe()
        return None

    def get_correlation(self):
        """Returns the correlation matrix."""
        if self.data is not None:
            # Select only numeric columns for correlation
            numeric_df = self.data.select_dtypes(include=[np.number])
            return numeric_df.corr()
        return None
