from components.asset import Asset
from components.ui.data_card import DataCard
import streamlit as st

ticker = st.session_state["ticker"]

@st.cache_data
def render_page():
    asset = Asset(ticker, interval="1mo")
    DataCard(asset).render("C-C")
    DataCard(asset).render("H-L")
    DataCard(asset).render("O-C")

if ticker != "":
    render_page()
else:
    st.write("No data to display")

