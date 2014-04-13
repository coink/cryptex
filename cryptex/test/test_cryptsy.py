import os
import io

import unittest
import httpretty
import requests

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

    def test_one(self):
        responses = {
            'allmytrades': 'all_my_trades.json',
            'getmarkets': 'get_markets.json'
        }
        with CryptsyMock(responses):
            trade = Cryptsy('key', 'secret').get_my_trades()[0]
            self.assertTrue(isinstance(trade, cryptex.trade.Buy))
            self.assertEqual(trade.trade_id, u'27208199')

if __name__ == '__main__':
    unittest.main()
