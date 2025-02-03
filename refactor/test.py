import streamlit as st
from ui import PageRenderer

st.set_page_config(layout="wide")

page = PageRenderer()

def daily_page(): return page.returns_page("SPY", "1d")
def weekly_page(): return page.returns_page("SPY", "5d")
def monthly_page(): return page.returns_page("SPY", "1mo")
def quarterly_page(): return page.returns_page("SPY", "3mo")

daily = st.Page(daily_page, title="Daily DoR")
weekly = st.Page(weekly_page, title="Weekly DoR")
monthly = st.Page(monthly_page, title="Monthly DoR")
quarterly = st.Page(quarterly_page, title="Quarterly DoR")

pg = st.navigation(
    {
        "Historical Volatility": [daily, weekly, monthly, quarterly]
    }
)

pg.run()
