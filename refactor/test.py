import streamlit as st
from ui import PageRenderer

st.set_page_config(layout="wide")


page = PageRenderer()

def daily_page(): return page.returns_page(ticker, "1d")
def weekly_page(): return page.returns_page(ticker, "5d")
def monthly_page(): return page.returns_page(ticker, "1mo")
def quarterly_page(): return page.returns_page(ticker, "3mo")

daily = st.Page(daily_page, title="Daily DoR")
weekly = st.Page(weekly_page, title="Weekly DoR")
monthly = st.Page(monthly_page, title="Monthly DoR")
quarterly = st.Page(quarterly_page, title="Quarterly DoR")

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
