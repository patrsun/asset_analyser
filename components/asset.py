from typing import Literal
import yfinance as yf
import numpy as np
import pandas as pd

class Asset():
    """
    Asset class to represent Bond ETFs, stocks, currencies, etc.

    Contains methods for calculating:
    - Distribution of Returns
    """
    def __init__(self, ticker: str, interval: Literal["1d", "1mo", "3mo"]="1d"):
        """
        Parameters 
        ----------
        ticker: str
            Ticker symbol for specified asset (i.e. AAPL, MSFT)

        interval: "1d", "1mo", "3mo"
            Time interval on which to analyse price data
                - 1d = 1 day (default)
                - 1mo = monthly
                - 3mo = quarterly
        """
        self.data = yf.Ticker(ticker).history(period="max", interval=interval, auto_adjust=False)
        # make Dates into their own column
        self.data.reset_index(inplace=True) 
        
        # calculate returns
        self.data["C-C"] = self.data["Adj Close"].pct_change()
        self.data["H-L"] = (self.data["High"] - self.data["Low"])/self.data["Low"]
        self.data["O-C"] = (self.data["Close"] - self.data["Open"])/self.data["Open"]

    def get_data(self):
        return self.data
    
    def returns_table(self, return_type:Literal["C-C", "H-L", "O-C"]):
        """
        Returns table of values for the specificed return type
        """
        # TODO: Work on special case for H-L returns

        # get column of returns
        returns = self.data[return_type]

        # descriptive stats
        mean = returns.mean()
        std = returns.std()
        total = returns.count()
        
        # generate distribution of returns table
        bins = np.arange(mean-(3*std), mean+(3*std)+0.001, 0.75*std)
        bins = np.concatenate(([-np.inf], bins, [np.inf]))
        table = pd.cut(returns, bins=bins, include_lowest=True)

        # count occurences 
        table = table.value_counts().sort_index().reset_index()

        # formatting
        table.columns=["Range", "Count"]
        table["Range"] = table["Range"].apply(self.__gen_label)

        # other statistics
        table["Probability"] = table["Count"]/total
        table["Cumulative Probability"] = table["Probability"].cumsum()
        table["Count"] = table["Count"].astype(str)
        table["Probability"] = table["Probability"].apply(self.__to_percent)
        table["Cumulative Probability"] = table["Cumulative Probability"].apply(self.__to_percent)
        
        return table
    
    def prob_table(self, return_type: Literal["C-C", "H-L", "O-C"]):
        returns = self.data[return_type] 
        total = returns.count()
        positive_points = returns[returns > 0]
        pos_count = positive_points.count()
        negative_points = returns[returns < 0]
        neg_count = negative_points.count()
        zero_points = returns[returns == 0]
        zero_count = zero_points.count()

        data = {
            "Average Returns": [positive_points.mean(), negative_points.mean(), 0],
            "Count": [pos_count, neg_count, zero_count],
            "Frequency %": [pos_count/total, neg_count/total, zero_count/total],
        }

        prob_table = pd.DataFrame(data, index=["Positive Data Points", "Negative Data Points", "Zero"])
        prob_table["Frequency Adjusted Returns"] = prob_table["Average Returns"] * prob_table["Frequency %"]
        prob_table["Average Returns"] = prob_table["Average Returns"].apply(self.__to_percent)
        prob_table["Count"] = prob_table["Count"].astype(str)
        prob_table["Frequency %"] = prob_table["Frequency %"].apply(self.__to_percent)
        prob_table["Frequency Adjusted Returns"] = prob_table["Frequency Adjusted Returns"].apply(self.__to_percent)

        return prob_table

    def var_table(self, return_type: Literal["C-C", "H-L", "O-C"]):
        """
        Table of upper bounds and lower bounds 1-3 standard deviations
        """
        returns = self.data[return_type]
        mean = returns.mean()
        std = returns.std()
        total = returns.count()
        
        data = {
            "Std Dev": [1, 2, 3],
            "Upper Bound": [mean + std, mean + 2*std, mean + 3*std],
            "Lower Bound": [mean - std, mean - (2*std), mean - (3*std)]
        }

        table = pd.DataFrame(data)
        table["Count"] = table.apply(
            lambda row: ((returns >= row["Lower Bound"]) & (returns <= row["Upper Bound"])).sum(),
            axis=1
        )
        table["Count %"]= table["Count"]/total
        table["Upper Bound"] = table["Upper Bound"].apply(self.__to_percent)
        table["Lower Bound"] = table["Lower Bound"].apply(self.__to_percent)
        table["Count"] = table["Count"].astype(str)
        table["Count %"] = table["Count %"].apply(self.__to_percent)
        table["Normal Count %"] = ["68.27%", "95.45%", "99.73%"]
        
        return table

    def summary_stats(self, return_type: Literal["C-C", "H-L", "O-C"]):
        """
        Summary table of descriptive statistics
        """
        returns = self.data[return_type]
        summary = pd.DataFrame(
            index=[
                "mean", "median", "mode", "std_dev", 
                "range", "max", "min", "count"
            ], 
            columns=["values"]
        )
        summary.loc["mean", "values"] = returns.mean()
        summary.loc["median", "values"] = returns.median()
        summary.loc["mode", "values"] = returns.mode().iat[0]
        summary.loc["std_dev", "values"] = returns.std()
        max = returns.max()
        min = returns.min()
        summary.loc["range", "values"] = max - min
        summary.loc["max", "values"] = max
        summary.loc["min", "values"] = min
        summary.loc["count", "values"] = returns.count()

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

