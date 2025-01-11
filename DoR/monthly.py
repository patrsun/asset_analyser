from components.asset import Asset
from components.ui.data_card import DataCard
import streamlit as st

ticker = st.session_state["ticker"]

@st.cache_data
def render_page(ticker):
    asset = Asset(ticker, interval="1mo")
    DataCard(asset).render("C-C")
    DataCard(asset).render("H-L")
    DataCard(asset).render("O-C")

if ticker != "":
    try:
        render_page(ticker)
    except: 
        st.write("Invalid ticker symbol")
else:
    st.write("No data to display")

