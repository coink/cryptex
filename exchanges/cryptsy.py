import time
import hmac
from hashlib import sha512
from urllib import urlencode
import datetime

import requests
import pytz

from exchanges.exchange import Exchange
from exchanges.trade import Trade

API_ENDPOINT = 'https://www.cryptsy.com/api'

class Cryptsy(Exchange):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.timezone = None

    def _get_timezone(self):
        """
        Cryptsy seems to return all its timestamps in Eastern Standard Time, 
        instead of doing the sane thing and returning UTC. But, the API does 
        not make this a guarantee, so we do a request for getinfo and get the 
        timezone then. We'll cache it, too.
        """
        if self.timezone is not None:
            return self.timezone

        info = self.get_info()
        return pytz.timezone(info['servertimezone'])

    def _convert_timestamp(self, time_str):
        """
        Convert cryptsy timestamp to timezone-aware datetime object in UTC
        """
        naive_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        cryptsy_time = self._get_timezone()
        aware_time = cryptsy_time.normalize(cryptsy_time.localize(naive_time)).astimezone(pytz.utc)
        return aware_time

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
        r = requests.post(API_ENDPOINT, data=payload, headers=headers)
        content = r.json()
        return content['return']
        
    def get_info(self):
        return self._perform_request('getinfo')

    def get_markets(self):
        return self._perform_request('getmarkets')

    def get_my_transactions(self):
        return self._perform_request('mytransactions')

    def get_trades(self, market_id):
        return self._perform_request('markettrades', {'marketid': market_id}) 

    def get_orders(self, market_id):
        return self._perform_request('marketorders', {'marketid': market_id}) 

    #def get_my_trades(self, market_id, limit=200):
    #    return self._perform_request('mytrades', {'marketid': market_id, 'limit': limit})

    def _format_trade(self, trade):
        if trade['tradetype'] == 'Buy':
            trade_type = Trade.BUY
        else:
            trade_type = Trade.SELL

        return Trade(
            trade_id = trade['tradeid'],
            trade_type = trade_type,
            primary_curr = None,
            secondary_curr = None,
            time = self._convert_timestamp(trade['datetime']),
            order_id = trade['order_id'],
            amount = trade['quantity'],
            price = trade['tradeprice'],
            fee = trade['fee']
        )

    def get_my_trades(self):
        trades = self._perform_request('allmytrades')
        return (trades, [self._format_trade(t) for t in trades])

    def get_my_orders(self, market_id):
        return self._perform_request('myorders', {'marketid': market_id})

    def get_all_my_orders(self):
        return self._perform_request('allmyorders')

    def get_depth(self, market_id):
        return self._perform_request('depth', {'marketid': market_id})

    def create_order(self, market_id, order_type, quantity, price):
        params = {
            'marketid': market_id,
            'ordertype': order_type,
            'quantity': quantity,
            'price': price
        }
        return self._perform_request('myorders', params)

    def cancel_order(self, order_id):
        return self._perform_request('cancelorder', {'orderid': order_id})

    def cancel_market_orders(self, market_id):
        return self._perform_request('cancelmarketorders', {'marketid': market_id})

    def cancel_all_orders(self):
        return self._perform_request('cancelallorders')

    def calculate_fees(self, order_type, quantity, price):
        params = {
            'ordertype': order_type,
            'quantity': quantity,
            'price': price
        }
        return self._perform_request('calculatefees', params)

    def generate_new_address(self, currency):
        if isinstance(currency, int):
            params = {'currencyid': currency}
        else:
            params = {'currencycode': currency}
        return self._perform_request('generatenewaddress', params)
