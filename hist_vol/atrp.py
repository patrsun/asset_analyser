from components.asset import Asset
import streamlit as st

asset = Asset("^GSPC")
st.dataframe(asset.atrp())
