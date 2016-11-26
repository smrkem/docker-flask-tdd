import unittest, json
from unittest.mock import patch
from flask_testing import TestCase
from stockdata import app


class HomeViewTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_home_view_calls_index_template(self):
        self.client.get('/')
        self.assert_template_used('index.html')

    @patch('stockdata.views.StockData')
    def test_stockdata_init_with_posted_symbol(self, mock_stockdata):
        response = self.client.post('/', data={'symbol': 'ANYSYMBOL'})
        mock_stockdata.assert_called_with('ANYSYMBOL')

    @patch('stockdata.views.StockData')
    def test_posting_symbol_returns_formatted_stock_info(self, mock_stockdata):
        mock_stockdata.return_value.get_stock_info.return_value = {"stock":"data"}
        mock_stockdata.return_value.get_pv_trend_data.return_value = ["date1 price data", "date2 price data"]
        response = self.client.post('/', data={'symbol': 'ANYSYMBOL'})

        self.assertEqual(response.status_code, 200)
        mock_stockdata.return_value.get_stock_info.assert_called_with()
        mock_stockdata.return_value.get_pv_trend_data.assert_called_with()
        expected_stock = {
            "stock":"data",
            "pv_trend_data": json.dumps(["date1 price data", "date2 price data"])
        }
        self.assertEqual(self.get_context_variable('stock'), expected_stock)

    @patch('stockdata.views.StockData')
    def test_posting_invalid_symbol_returns_error(self, mock_stockdata):
        mock_stockdata.return_value.get_stock_info.return_value = None
        response = self.client.post('/', data={'symbol': 'not-valid'})

        errors = ["Could not find any stock for symbol: 'not-valid'"]
        self.assertEqual(self.get_context_variable('errors'), errors)
        mock_stockdata.return_value.get_stock_info.assert_called_with()


if __name__ == '__main__':
    unittest.main()
