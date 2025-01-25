from components.asset import Asset
from components.ui.data_card import DataCard
import streamlit as st

st.set_page_config(layout="wide")

daily = st.Page("DoR/daily.py", title="Daily DoR")
weekly = st.Page("DoR/weekly.py", title="Weekly DoR")
monthly = st.Page("DoR/monthly.py", title="Monthy DoR")
quarterly = st.Page("DoR/quarterly.py", title="Quarterly DoR")

pg = st.navigation(
    {
        "Historical Volatility": [daily, weekly, monthly, quarterly]
    }
)

with st.sidebar:
    ticker = st.text_input(
        "Enter ticker symbol",
        key="ticker"
    )

pg.run()

