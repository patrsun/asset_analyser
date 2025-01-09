from components.asset import Asset
from components.ui.data_card import DataCard
import streamlit as st

st.set_page_config(layout="wide")

asset = Asset("MSFT", interval="3mo")
DataCard(asset).render("C-C")
