from components.asset import Asset
from components.ui.data_card import DataCard
import streamlit as st

st.set_page_config(layout="wide")

asset = Asset("NVDA", interval="1mo")
DataCard(asset).render("C-C")
DataCard(asset).render("H-L")
DataCard(asset).render("O-C")
