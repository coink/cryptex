import time
import hmac
from hashlib import sha512
from urllib import urlencode
import requests

class Cryptsy:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def get_request_params(self, method, data):
        payload = {
            'method': method,
            'nonce': int(time.time())
        }
        payload.update(data)
        signature = hmac.new(self.secret, urlencode(payload), 
            sha512).hexdigest()
        
        headers = {
            'Sign': signature, 
            'Key': self.key
        }
        return (payload, headers)

    def _perform_request(self, method, data={}):
        payload, headers = self.get_request_params(method, data)
        r = requests.post('https://www.cryptsy.com/api', data=payload, headers=headers)
        print r.headers
        content = r.json()
        return content['return']
        
    def get_info(self):
        pass

    def get_markets(self):
        return self._perform_request('getmarkets')

    def get_my_transaction(self):
        pass

    def get_trades(self, market_id):
        return self._perform_request('markettrades', {'marketid': market_id}) 

    def get_orders(self, market_id):
        return self._perform_request('marketorders', {'marketid': market_id}) 

    def get_my_trades(self, market_id, limit=200)
        return self._perform_request('mytrades', {'marketid': market_id, 'limit': limit})

    def get_all_my_trades(self):
        pass

    def get_my_orders(self, market_id):
        pass

    def get_depth(self, market_id):
        pass

    def get_all_my_orders(self):
        pass

    def create_order(self, market_id, order_type, quantity, price):
        pass

    def cancel_order(self, order_id):
        pass

    def cancel_market_orders(self, market_id):
        pass

    def cancel_all_orders(self):
        pass

    def calculate_fees(self, order_type, quantity, price):
        pass

    def generate_new_address(self, currency):
        pass
