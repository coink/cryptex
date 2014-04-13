import os
import io
from datetime import datetime
from decimal import Decimal
import unittest

import httpretty
import requests
import pytz

from cryptex.exchange import Cryptsy
import cryptex.trade

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

    def test_trades(self):
        responses = {
            'allmytrades': 'all_my_trades.json',
            'getmarkets': 'get_markets.json'
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

if __name__ == '__main__':
    unittest.main()
