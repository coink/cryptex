import datetime
from decimal import Decimal

import pytz

from exchanges.exchange import Exchange
from exchanges.trade import Trade
from exchanges.signed_single_endpoint import SignedSingleEndpoint

class Cryptsy(Exchange, SignedSingleEndpoint):
    API_ENDPOINT = 'https://www.cryptsy.com/api'
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.timezone = None
        self.market_currency_map = None

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

    def _get_currencies(self, market_id):
        """
        Cryptsy uses references to market_ids which uniquely identify markets.
        Given a market_id, this function returns a two-tuple containing the currencies involved.
        """
        if self.market_currency_map is None:
            markets = self.get_markets()
            self.market_currency_map = {
                m['marketid']:
                (m['primary_currency_code'], m['secondary_currency_code'])
                for m in markets
            }
        return self.market_currency_map[market_id]

    def get_info(self):
        return self.perform_request('getinfo')

    def get_markets(self):
        return self.perform_request('getmarkets')

    def get_my_transactions(self):
        return self.perform_request('mytransactions')

    def get_trades(self, market_id):
        return self.perform_request('markettrades', {'marketid': market_id}) 

    def get_orders(self, market_id):
        return self.perform_request('marketorders', {'marketid': market_id}) 

    #def get_my_trades(self, market_id, limit=200):
    #    return self.perform_request('mytrades', {'marketid': market_id, 'limit': limit})

    def _format_trade(self, trade):
        if trade['tradetype'] == 'Buy':
            trade_type = Trade.BUY
        else:
            trade_type = Trade.SELL

        primary, secondary = self._get_currencies(trade['marketid'])

        return Trade(
            trade_id = trade['tradeid'],
            trade_type = trade_type,
            primary_curr = primary,
            secondary_curr = secondary,
            time = self._convert_timestamp(trade['datetime']),
            order_id = trade['order_id'],
            amount = Decimal(trade['quantity']),
            price = Decimal(trade['tradeprice']),
            fee = Decimal(trade['fee'])
        )

    def get_my_trades(self):
        trades = self.perform_request('allmytrades')
        return [self._format_trade(t) for t in trades]

    def get_my_orders(self, market_id):
        return self.perform_request('myorders', {'marketid': market_id})

    def get_my_open_orders(self):
        orders = self.perform_request('allmyorders')
        return orders

    def get_depth(self, market_id):
        return self.perform_request('depth', {'marketid': market_id})

    def create_order(self, market_id, order_type, quantity, price):
        params = {
            'marketid': market_id,
            'ordertype': order_type,
            'quantity': quantity,
            'price': price
        }
        return self.perform_request('myorders', params)

    def cancel_order(self, order_id):
        return self.perform_request('cancelorder', {'orderid': order_id})

    def cancel_market_orders(self, market_id):
        return self.perform_request('cancelmarketorders', {'marketid': market_id})

    def cancel_all_orders(self):
        return self.perform_request('cancelallorders')

    def calculate_fees(self, order_type, quantity, price):
        params = {
            'ordertype': order_type,
            'quantity': quantity,
            'price': price
        }
        return self.perform_request('calculatefees', params)

    def generate_new_address(self, currency):
        if isinstance(currency, int):
            params = {'currencyid': currency}
        else:
            params = {'currencycode': currency}
        return self.perform_request('generatenewaddress', params)
