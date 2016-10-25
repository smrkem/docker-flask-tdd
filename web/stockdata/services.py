class StockData:

    def __init__(self):
        self.stockdata = {
            "AETI": {
                "symbol": "AETI",
                "name": "American Electric Technologies Inc",
                "exchange": "NASDAQ"
            },
            "CRNT": {
                "symbol": "CRNT",
                "name": "Ceragon Networks Ltd",
                "exchange": "NASDAQ"
            }
        }

    def get_stock_info(self, symbol):
        return self.stockdata.get(symbol)