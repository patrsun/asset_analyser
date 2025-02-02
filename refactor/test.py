from asset import Asset
from asset_historical import AssetHistorical

SPY = Asset("SPY")
data = AssetHistorical(SPY, "1d")

print(data.probablities("C-C"))
