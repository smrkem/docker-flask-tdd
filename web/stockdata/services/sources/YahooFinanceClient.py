from yahoo_finance import Share


class YahooFinanceClient:

    def get_stock_info(self, symbol):
        stock = Share(symbol)
        stock_name = stock.get_name()
        if stock_name is None:
            return None

        stock_exchange = stock.get_stock_exchange()
        return {
            "symbol": symbol,
            "name": stock_name,
            "exchange": stock_exchange
        }
