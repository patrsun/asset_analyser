from asset import Asset
from asset_historical import AssetHistorical

import streamlit as st

SPY = Asset("SPY")
data = AssetHistorical(SPY, "1d")

print(data.atrp())
