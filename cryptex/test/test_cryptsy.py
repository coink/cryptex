import os
import io
import unittest
import httpretty
import requests

test_dir = os.path.dirname(os.path.realpath(__file__))
mock_dir = os.path.join(test_dir, 'mocks')

class CryptsyMock():
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        httpretty.enable()
        with io.open(os.path.join(mock_dir, self.filename), 'r') as f:
            contents = f.read()
            httpretty.register_uri(httpretty.GET, "https://api.cryptsy.com/api",
                                   body=contents)

    def __exit__(self, type, value, traceback):
        httpretty.disable()
        httpretty.reset()


class TestCryptsyPrivate(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one(self):
        with CryptsyMock('all_my_trades.json'):
            response = requests.get('https://api.cryptsy.com/api')
            content = response.json() 
            self.assertEqual(content['success'], "1")

if __name__ == '__main__':
    unittest.main()
