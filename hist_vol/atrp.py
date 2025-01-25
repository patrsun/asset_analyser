from components.asset import Asset
import pandas as pd
import streamlit as st

def to_percent(x):
    return f"{x*100:.2f}%"

dat = Asset("^GSPC").data

dat["Previous Close"] = dat["Close"].shift(1)
def atrp(row):
    # check for NaN values
    if row["Previous Close"] != row["Previous Close"]:
        return None
    else:
        return max(row["High"] - row["Low"],
                abs(row["High"] - row["Previous Close"]), 
                abs(row["Low"]- row["Previous Close"]))/row["Close"]

dat["ATRP"] = dat.apply(atrp, axis=1)

td = [5, 20, 60, 250, 750, 1250, 2500, 5000, 12500]
atrp = [dat["ATRP"].tail(x).mean() for x in td]

data = {
    "Trading Days": [str(x) for x in td],
    "Horizon": ["1 Week", "1 Month", "3 Months", "1 Year", "3 Years", "5 Years", "10 Years", "20 Years", "50 Years"],
    "Average Daily True Range %": atrp
}

ATRP = pd.DataFrame(data)

ATRP["Average Daily True Range %"] = ATRP["Average Daily True Range %"].apply(to_percent)

ATRP
