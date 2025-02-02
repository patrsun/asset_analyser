import pandas as pd
import numpy as np
from asset import Asset

class AssetHistorical():
    def __init__(self, asset: Asset, interval):
        self.asset = asset
        
        self.data = asset.history(interval=interval)
        self.data.reset_index(inplace=True)

        # calculate returns
        self.data["C-C"] = self.data["Adj Close"].pct_change()
        self.data["H-L"] = (self.data["High"] - self.data["Low"])/self.data["Low"]
        self.data["O-C"] = (self.data["Close"] - self.data["Open"])/self.data["Open"]

        # remove all invalid data rows
        invalid_rows = self.data[np.isinf(self.data["O-C"])].index

        if (not invalid_rows.empty):
            max_invalid = invalid_rows.max()
            self.data.drop(self.data.index[:max_invalid+1], inplace=True)
    
    # DISTRIBUTION OF RETURNS
    # --------------------------
    def returns(self, return_type):
        returns = self.data[return_type]

        # stats for bins
        mean = returns.mean()
        std = returns.std()
        total = returns.count()

        # generate bins
        bins = np.arange(mean-(3*std), mean+(3*std)+0.001, 0.75*std)
        bins = np.concatenate(([-np.inf], bins, [np.inf]))
        table = pd.cut(returns, bins=bins, include_lowest=True)

        freq_table = table.value_counts().sort_index().reset_index()
        freq_table.columns=["Range", "Count"]
        freq_table["Probability"] = freq_table["Count"]/total

        return pd.DataFrame({
            "Range": freq_table["Range"].apply(self.__gen_label),
            "Probability": freq_table["Probability"].apply(self.__to_percent),
            "Cumulative Probability": freq_table["Probability"].cumsum().apply(self.__to_percent),
            "Count": freq_table["Count"].astype(str),
        })
    
    def probablities(self, return_type):
        returns = self.data[return_type] 
        total = returns.count()

        positive_points = returns[returns > 0]
        pos_count = positive_points.count()

        negative_points = returns[returns < 0]
        neg_count = negative_points.count()

        zero_points = returns[returns == 0]
        zero_count = zero_points.count()

        avg_returns = pd.Series([positive_points.mean(), negative_points.mean(), 0])
        counts = pd.Series([pos_count, neg_count, zero_count])
        freq = pd.Series([pos_count/total, neg_count/total, zero_count/total])
        
        table = pd.DataFrame({
            "Average Returns": avg_returns.apply(self.__to_percent),
            "Count": counts.astype(str),
            "Frequency %": freq.apply(self.__to_percent),
            "Frequency Adjusted Returns": (avg_returns * freq).apply(self.__to_percent)
        })
        
        table.index = ["Positive Data Points", "Negative Data Points", "Zero"]

        return table

    def variance(self, return_type):
        returns = self.data[return_type]

        mean = returns.mean()
        std = returns.std()
        total = returns.count()
            
        upper = pd.Series([mean + std, mean + 2*std, mean + 3*std])
        lower = pd.Series([mean - std, mean - (2*std), mean - (3*std)])
        count = pd.Series([
                ((returns >= (mean - i * std)) & (returns <= (mean + i * std))).sum() 
                for i in [1,2,3]
        ])

        return pd.DataFrame({
            "Std Dev": [1,2,3],
            "Upper Bound": upper.apply(self.__to_percent),
            "Lower Bound": lower.apply(self.__to_percent),
            "Count": count.astype(str),
            "Count %": (count/total).apply(self.__to_percent),
            "Normal Count %": ["68.27%", "95.45%", "99.73%"]
        })

    def summary(self, return_type):
        returns = self.data[return_type]
        summary = pd.DataFrame()

        summary.loc["mean", "values"] = self.__to_percent(returns.mean())
        summary.loc["standard deviation", "values"] = self.__to_percent(returns.std())
        summary.loc["kurtosis", "values"] = f"{returns.kurt():.3f}"
        summary.loc["skew", "values"] = f"{returns.skew():.3f}"
        max = returns.max()
        min = returns.min()
        summary.loc["max", "values"] = self.__to_percent(max)
        summary.loc["min", "values"] = self.__to_percent(min)
        summary.loc["range", "values"] = self.__to_percent(max - min)
        summary.loc["count", "values"] = str(returns.count())

        return summary

    @staticmethod
    def __gen_label(bin):
        """
        Generates labels for each interval
        """
        lower = bin.left
        upper = bin.right

        if lower == -np.inf: 
            return f'Less than {(upper * 100):.1f}%'
        if upper == np.inf:
            return f'Greater than {(lower * 100):.1f}%'
        
        return f"{(lower * 100):.1f}% to {(upper * 100):.1f}%"
    
    @staticmethod
    def __to_percent(x):
        return f"{x*100:.2f}%"


