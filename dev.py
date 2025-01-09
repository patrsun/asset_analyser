from components.asset import Asset
from components.ui.data_card import DataCard
import streamlit as st

st.set_page_config(layout="wide")

asset = Asset("AAPL", interval="1d")
DataCard(asset).render("C-C")
