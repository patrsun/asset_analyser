from typing import Literal
import yfinance as yf
import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None

class Asset():
    """
    Asset class to represent Bond ETFs, stocks, currencies, etc.

    Contains methods for calculating:
    - Distribution of Returns
    """
    def __init__(self, ticker: str, interval: Literal["1d", "5d", "1mo", "3mo"]="1d"):
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
        asset = yf.Ticker(ticker) 
        self.name = asset.info["longName"]
        self.interval = interval

        self.data = asset.history(
            period="max", 
            interval=interval, 
            auto_adjust=False
        ).tz_localize(None)
        
        self.calculate_returns()
        self.calculate_atrp()
        
        # get start and end date of data
        self.start_date = self.data.index.min()
        self.end_date = self.data.index.max()

    def calculate_returns(self):
        self.data["C-C"] = self.data["Adj Close"].pct_change()
        self.data["H-L"] = (self.data["High"] - self.data["Low"])/self.data["Low"]
        self.data["O-C"] = (self.data["Close"] - self.data["Open"])/self.data["Open"]
        
        # remove all invalid rows of data
        invalid_rows = self.data[np.isinf(self.data["O-C"])].index
        
        if (not invalid_rows.empty):
            max_invalid = invalid_rows.max()
            self.data.drop(self.data.index[:max_invalid+1], inplace=True)

    def calculate_atrp(self):
        data = self.data[["High", "Low", "Close"]]
        data["Previous Close"] = data["Close"].shift(1)

        def atrp(row):
            # check for NaN values
            if row["Previous Close"] != row["Previous Close"]:
                return None
            else:
                return max(row["High"] - row["Low"],
                        abs(row["High"] - row["Previous Close"]), 
                        abs(row["Low"]- row["Previous Close"]))/row["Close"]
        
        self.data["ATRP"] = data.apply(atrp, axis=1)

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
        freq_table = pd.cut(returns, bins=bins, include_lowest=True)

        # count occurences 
        freq_table = freq_table.value_counts().sort_index().reset_index()

        # formatting
        freq_table.columns=["Range", "Count"]
        freq_table["Probability"] = freq_table["Count"]/total
        
        return pd.DataFrame({
            "Range": freq_table["Range"].apply(self.__gen_label),
            "Count": freq_table["Count"].astype(str),
            "Probability": freq_table["Probability"].apply(self.__to_percent),
            "Cumulative Probability": freq_table["Probability"].cumsum().apply(self.__to_percent)
        })
    
    def prob_table(self, return_type: Literal["C-C", "H-L", "O-C"]):
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
        freqs = pd.Series([pos_count/total, neg_count/total, zero_count/total])

        table = pd.DataFrame({
            "Average Returns": avg_returns.apply(self.__to_percent),
            "Count": counts.astype(str),
            "Frequency %": freqs.apply(self.__to_percent),
            "Frequency Adjusted Returns": (avg_returns * freqs).apply(self.__to_percent)
        })

        table.index = ["Positive Data Points", "Negative Data Points", "Zero"]

        return table

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

        upper = [mean + std, mean + 2*std, mean + 3*std]
        lower = [mean - std, mean - (2*std), mean - (3*std)]

        counts = pd.Series([((returns >= low) & (returns <= high)).sum() 
            for low, high in zip(lower, upper)])

        return pd.DataFrame({
            "Std Dev": [1,2,3],
            "Upper Bound": upper,
            "Lower Bound": lower,
            "Count": counts.astype(str),
            "Count %": (counts/total).apply(self.__to_percent),
            "Normal Count %": ["68.27%", "95.45%", "99.73%"]
        })

    def summary_stats(self, return_type: Literal["C-C", "H-L", "O-C"]):
        """
        Summary table of descriptive statistics
        """
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

    def atrp_table(self):
        """
        Returns Average True Range Percentage Table
        """
        data = self.data[["High", "Low", "Close"]]
        data["Previous Close"] = data["Close"].shift(1)

        def atrp(row):
            # check for NaN values
            if row["Previous Close"] != row["Previous Close"]:
                return None
            else:
                return max(row["High"] - row["Low"],
                        abs(row["High"] - row["Previous Close"]), 
                        abs(row["Low"]- row["Previous Close"]))/row["Close"]
        
        data["ATRP"] = data.apply(atrp, axis=1)

        match self.interval:
            case "1d": 
                timeframe = "Daily"
                periods = [5, 20, 60, 250, 750, 1250, 2500, 5000, 12500]
                horizon = ["1 Week", "1 Month", "1 Quarter", "1 Year", "3 Years", "5 Years", "10 Years", "20 Years", "50 Years"]

            case "5d":
                timeframe = "Weekly"
                periods = [4, 12, 52, 156, 260, 520, 1040, 2600]
                horizon = ["1 Month", "1 Quarter", "1 Year", "3 Years", "5 Years", "10 Years", "20 Years", "50 Years"]

            case "1mo":
                timeframe = "Monthly"
                periods = [3, 12, 36, 60, 120, 240, 600]
                horizon = ["1 Quarter", "1 Year", "3 Years", "5 Years", "10 Years", "20 Years", "50 Years"]

            case "3mo":
                timeframe = "Quarterly"
                periods = [4, 12, 20, 40, 80, 200]
                horizon = ["1 Year", "3 Years", "5 Years", "10 Years", "20 Years", "50 Years"]
        
        atrp_table = pd.DataFrame({
            "Trading Periods": [str(p) for p in periods],
            "Horizon": horizon,
            f"Average {timeframe} True Range %": [f"{data["ATRP"].tail(p).mean()*100:.2f}%" for p in periods]
        })

        return atrp_table
        
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

