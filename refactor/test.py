from asset import Asset
from asset_historical import AssetHistorical

import streamlit as st

SPY = Asset("SPY")
data = AssetHistorical(SPY, "1d")

st.write(data.variance("C-C"))
