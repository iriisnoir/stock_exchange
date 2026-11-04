import unittest
from main import StockExchange, LimitOrder, MarketOrder

class TestStockExchange(unittest.TestCase):
    def setUp(self):
        self.exchange = StockExchange()

    def test_limit_order_statuses(self):
        order = LimitOrder("BUY", "SNAP", "LMT", "$30.00", "10")
        self.assertEqual(order._status, "PENDING")

        order._filled_shares = 5
        order.order_status()
        self.assertEqual(order._status, "PARTIAL")

        order._filled_shares = 10
        order.order_status()
        self.assertEqual(order._status, "FILLED")

    def test_matching(self):
        buy_order = LimitOrder("BUY", "SNAP", "LMT", "$30.00", "10")
        sell_order = LimitOrder("SELL", "SNAP", "LMT", "$29.99", "5")

        self.exchange.place_order(buy_order)
        self.exchange.place_order(sell_order)

        self.assertEqual(sell_order._status, "FILLED")
        self.assertEqual(buy_order._filled_shares, 5)
        self.assertEqual(buy_order._status, "PARTIAL")

    def test_quote_order_empty(self):
        ticker_buy = [order for order in self.exchange.buy_order if order._name == "SNAP"]
        self.assertEqual(len(ticker_buy), 0)

        self.assertIsNone(self.exchange.last_prices.get("SNAP"))