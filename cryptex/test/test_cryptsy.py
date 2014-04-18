import os
import io
from datetime import datetime
from decimal import Decimal
import unittest

import httpretty
import requests
import pytz

from cryptex.exchange import Cryptsy
from cryptex.exception import APIException
import cryptex.trade
import cryptex.order
import cryptex.transaction

test_dir = os.path.dirname(os.path.realpath(__file__))
mock_dir = os.path.join(test_dir, 'mocks')

class CryptsyMock():
    """
    Responses should be a {method: filename} map
    """
    def __init__(self, responses):
        self.responses = responses

    def request_callback(self, request, uri, headers):
        method = request.parsed_body[u'method'][0]
        filename = self.responses[method]
        with io.open(os.path.join(mock_dir, filename), 'r') as f:
            contents = f.read()
        return (200, headers, contents)

    def __enter__(self):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST, "https://api.cryptsy.com/api",
                               body=self.request_callback)

    def __exit__(self, type, value, traceback):
        httpretty.disable()
        httpretty.reset()


class TestCryptsyPrivate(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_markets(self):
        responses = {
            'getmarkets': 'get_markets.json',
        }
        with CryptsyMock(responses):
            markets = Cryptsy('key', 'secret').get_markets()
        self.assertEqual(len(markets), 3)
        self.assertIn(('DOGE', 'LTC'), markets)
        self.assertIn(('LTC', 'BTC'), markets)
        self.assertIn(('DOGE', 'BTC'), markets)

    def test_trades(self):
        responses = {
            'allmytrades': 'all_my_trades.json',
            'getmarkets': 'get_markets.json',
        }
        with CryptsyMock(responses):
            trade = Cryptsy('key', 'secret').get_my_trades()[0]
        self.assertTrue(isinstance(trade, cryptex.trade.Buy))
        self.assertEqual(trade.trade_id, u'27208199')
        self.assertEqual(trade.order_id, u'52078792')
        self.assertEqual(trade.base_currency, u'DOGE')
        self.assertEqual(trade.counter_currency, u'BTC')
        self.assertEqual(trade.datetime, datetime(2014, 3, 2, 4, 4, 29, tzinfo=pytz.timezone('US/Eastern')))
        self.assertEqual(trade.amount, Decimal('62661.89842537'))
        self.assertEqual(trade.price, Decimal('0.00000180'))
        self.assertEqual(trade.fee, Decimal('0.000225580'))

    def test_empty_open_orders(self):
        responses = {
            'allmyorders': 'all_my_orders_empty.json',
        }
        with CryptsyMock(responses):
            orders = Cryptsy('key', 'secret').get_my_open_orders()
        self.assertEqual(len(orders), 0)

    def test_open_orders(self):
        responses = {
            'allmyorders': 'all_my_orders.json',
            'getmarkets': 'get_markets.json',
        }
        with CryptsyMock(responses):
            orders = Cryptsy('key', 'secret').get_my_open_orders()
        self.assertEqual(len(orders), 2)
        sell_order, buy_order = orders

        self.assertTrue(isinstance(sell_order, cryptex.order.SellOrder))
        self.assertEqual(sell_order.order_id, u'76424299')
        self.assertEqual(sell_order.base_currency, u'DOGE')
        self.assertEqual(sell_order.counter_currency, u'BTC')
        self.assertEqual(sell_order.datetime, datetime(2014, 4, 16, 1, 18, 6, tzinfo=pytz.timezone('US/Eastern')))
        self.assertEqual(sell_order.price, Decimal('0.00000200'))
        self.assertEqual(sell_order.amount, Decimal('10000.00000000'))

        self.assertTrue(isinstance(buy_order, cryptex.order.BuyOrder))
        self.assertEqual(buy_order.order_id, u'76433518')
        self.assertEqual(buy_order.base_currency, u'DOGE')
        self.assertEqual(buy_order.counter_currency, u'BTC')
        self.assertEqual(buy_order.datetime, datetime(2014, 4, 16, 1, 34, 14, tzinfo=pytz.timezone('US/Eastern')))
        self.assertEqual(buy_order.price, Decimal('0.00000120'))
        self.assertEqual(buy_order.amount, Decimal('94.93989121'))

    def test_cancel_order(self):
        responses = {
            'cancelorder': 'cancel_order_success.json',
        }
        with CryptsyMock(responses):
            Cryptsy('key', 'secret').cancel_order(u'12345')

    def test_cancel_order_fail(self):
        responses = {
            'cancelorder': 'cancel_order_failure.json',
        }
        with CryptsyMock(responses):
            c = Cryptsy('key', 'secret')
            self.assertRaises(APIException, c.cancel_order, u'12345')

    def test_buy(self):
        responses = {
            'createorder': 'buy_order.json',
            'getmarkets': 'get_markets.json',
        }
        with CryptsyMock(responses):
            market = ('DOGE', 'BTC')
            amount = "94.93989121"
            price = "0.00000120"
            c = Cryptsy('key', 'secret')
            order_id = c.buy(market, amount, price)
        self.assertEqual(order_id, u'76447016')

    def test_sell(self):
        responses = {
            'createorder': 'sell_order.json',
            'getmarkets': 'get_markets.json',
        }
        with CryptsyMock(responses):
            market = ('LTC', 'BTC')
            amount = "10000"
            price = "0.00000200"
            c = Cryptsy('key', 'secret')
            order_id = c.sell(market, amount, price)
        self.assertEqual(order_id, u'76450269')

    def test_get_balances(self):
        responses = {
            'getinfo': 'get_info.json'
        }
        with CryptsyMock(responses):
            c = Cryptsy('key', 'secret')
            balances = c.get_my_balances()
        self.assertEqual(balances['Points'], Decimal('0.10721000'))
        self.assertEqual(balances['DOGE'], Decimal('42561.89842537'))

    def test_get_transactions(self):
        responses = {
            'mytransactions': 'my_transactions.json'
        }
        with CryptsyMock(responses):
            c = Cryptsy('key', 'secret')
            transactions = c.get_my_transactions()
        self.assertEquals(len(transactions), 3)
        tx = transactions[0]
        self.assertTrue(isinstance(tx, cryptex.transaction.Transaction))
        self.assertEqual(tx.amount, Decimal("0.00902000"))
        self.assertEqual(tx.currency, u"Points")
        self.assertEqual(tx.datetime, datetime(2014, 3, 3, 9, 7, 14, tzinfo=pytz.utc))
        self.assertEqual(tx.fee, Decimal("0.00000000"))
        self.assertEqual(tx.address, None)

        tx = transactions[1]
        self.assertTrue(isinstance(tx, cryptex.transaction.Withdrawal))
        self.assertEqual(tx.amount, Decimal("0.11661477"))
        self.assertEqual(tx.currency, u"BTC")
        self.assertEqual(tx.datetime, datetime(2014, 1, 20, 23, 2, 52, tzinfo=pytz.utc))
        self.assertEqual(tx.fee, Decimal("0.00050000"))
        self.assertEqual(tx.address, u'3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy')
        self.assertEqual(tx.transaction_id, u'b9B45AC6C3cB5Ab9DC2ad33CE76353c0c0AcDB59b8Edd6c3f62cbFdf78bAAE35')

        tx = transactions[2]
        self.assertTrue(isinstance(tx, cryptex.transaction.Deposit))
        self.assertEqual(tx.amount, Decimal("2463.57149311"))
        self.assertEqual(tx.currency, u"DOGE")
        self.assertEqual(tx.datetime, datetime(2013, 12, 23, 7, 52, 28, tzinfo=pytz.utc))
        self.assertEqual(tx.fee, Decimal("0.00000000"))
        self.assertEqual(tx.address, u'DJ98t1WpEZ73CNmQviecrnyiWrnqRhWNLy')
        self.assertEqual(tx.transaction_id, u'B2b1a19A6A27907cdfd422f3fbBd57cdC36fbdb121Cd5aFbaE1A738aD7B151a4')

if __name__ == '__main__':
    unittest.main()
