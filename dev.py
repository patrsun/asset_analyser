from components.asset import Asset
import streamlit as st

st.write(Asset("MSFT").get_data())
st.dataframe(Asset("MSFT").returns_table("C-C"))
