import yfinance as yf

class Asset():
    def __init__(self, ticker):
        self.__asset = yf.Ticker(ticker)

    def history(self, period="max", interval="1d"):
        return self.__asset.history(
            period=period, 
            interval=interval,
            auto_adjust=False,
        ).tz_localize(None)

    def info(self):
        return self.__asset.info
    
