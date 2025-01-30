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
        self.name = asset.info["shortName"]
        self.interval = interval
        self.data = asset.history(period="max", interval=interval, auto_adjust=False)
        # make Dates into their own column
        self.data.reset_index(inplace=True) 
        
        # calculate returns
        self.data["C-C"] = self.data["Adj Close"].pct_change()
        self.data["H-L"] = (self.data["High"] - self.data["Low"])/self.data["Low"]
        self.data["O-C"] = (self.data["Close"] - self.data["Open"])/self.data["Open"]
        
        # remove all invalid rows of data
        invalid_rows = self.data[np.isinf(self.data["O-C"])].index
        
        if (not invalid_rows.empty):
            max_invalid = invalid_rows.max()
            self.data.drop(self.data.index[:max_invalid+1], inplace=True)
        
        # get start and end date of data
        self.start_date = self.data["Date"].min()
        self.end_date = self.data["Date"].max()

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
        summary = pd.DataFrame()
        summary.loc["mean", "values"] = self.__to_percent(returns.mean())
        # summary.loc["median", "values"] = self.__to_percent(returns.median())
        # summary.loc["mode", "values"] = self.__to_percent(returns.mode().iat[0])
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

    def atrp(self):
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

