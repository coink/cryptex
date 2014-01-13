import datetime
from decimal import Decimal

import pytz

from cryptex.exchange import Exchange
from cryptex.trade import Trade
from cryptex.order import Order
from cryptex.single_endpoint import SignedSingleEndpoint

class Cryptsy(Exchange, SignedSingleEndpoint):
    API_ENDPOINT = 'https://www.cryptsy.com/api'
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.timezone = None
        self.market_currency_map = None
        self.pair_market_map = None

    def _get_timezone(self):
        """
        Cryptsy seems to return all its timestamps in Eastern Standard Time, 
        instead of doing the sane thing and returning UTC. But, the API does 
        not make this a guarantee, so we do a request for getinfo and get the 
        timezone then. We'll cache it, too.
        """
        if self.timezone is not None:
            return self.timezone

        info = self._get_info()
        return pytz.timezone(info['servertimezone'])

    def _convert_timestamp(self, time_str):
        """
        Convert cryptsy timestamp to timezone-aware datetime object in UTC
        """
        naive_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        cryptsy_time = self._get_timezone()
        aware_time = cryptsy_time.normalize(cryptsy_time.localize(naive_time)).astimezone(pytz.utc)
        return aware_time

    def _get_market_currency_map(self):
        if self.market_currency_map is None:
            markets = self.perform_request('getmarkets')
            self.market_currency_map = {
                m['marketid']:
                (m['primary_currency_code'], m['secondary_currency_code'])
                for m in markets
            }
        return self.market_currency_map

    def _get_pair_market_map(self):
        if self.pair_market_map is None:
            markets = self.perform_request('getmarkets')
            self.pair_market_map = {
                (m['primary_currency_code'], m['secondary_currency_code']):
                m['marketid']
                for m in markets
            }
        return self.pair_market_map

    def _get_currencies(self, market_id):
        """
        Cryptsy uses references to market_ids which uniquely identify markets.
        Given a market_id, this function returns a two-tuple containing the currencies involved.
        """
        return self._get_market_currency_map()[market_id]

    def _get_market_id(self, pair):
        return self._get_pair_market_map()[pair]

    def _get_info(self):
        return self.perform_request('getinfo')

    def get_markets(self):
        markets = self.perform_request('getmarkets')
        return [
            (m['primary_currency_code'], m['secondary_currency_code']) 
            for m in markets
        ]

    def _format_trade(self, trade):
        if trade['tradetype'] == 'Buy':
            trade_type = Trade.BUY
        else:
            trade_type = Trade.SELL

        base, counter = self._get_currencies(trade['marketid'])

        return Trade(
            trade_id = trade['tradeid'],
            trade_type = trade_type,
            base_currency = base,
            counter_currency = counter,
            time = self._convert_timestamp(trade['datetime']),
            order_id = trade['order_id'],
            amount = Decimal(trade['quantity']),
            price = Decimal(trade['tradeprice']),
            fee = Decimal(trade['fee'])
        )

    def get_my_trades(self):
        trades = self.perform_request('allmytrades')
        return [self._format_trade(t) for t in trades]

    def _format_order(self, order):
        if order['ordertype'] == 'Buy':
            order_type = Trade.BUY
        else:
            order_type = Trade.SELL

        base, counter = self._get_currencies(order['marketid'])

        return Order(
            order_id = order['orderid'],
            order_type = order_type,
            base_currency = base,
            counter_currency = counter,
            time = self._convert_timestamp(order['created']),
            amount = Decimal(order['quantity']),
            price = Decimal(order['price'])
        )

    def get_my_open_orders(self):
        orders = self.perform_request('allmyorders')
        return [self._format_order(o) for o in orders]

    def cancel_order(self, order_id):
        self.perform_request('cancelorder', {'orderid': order_id})
        return None


    def _create_order(self, market_id, order_type, quantity, price):
        params = {
            'marketid': market_id,
            'ordertype': order_type,
            'quantity': quantity,
            'price': price
        }
        return self.perform_request('createorder', params)

    def buy(self, market, quantity, price):
        market_id = self._get_market_id(market)
        response = self._create_order(market_id, 'Buy', quantity, price)
        return response['orderid']

    def sell(self, market, quantity, price):
        market_id = self._get_market_id(market)
        response = self._create_order(market_id, 'Sell', quantity, price)
        return response['orderid']
