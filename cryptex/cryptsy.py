import datetime
from decimal import Decimal, InvalidOperation

import pytz

from cryptex.exchange import Exchange
from cryptex.trade import Trade
from cryptex.order import Order
from cryptex.single_endpoint import SingleEndpoint, SignedSingleEndpoint


class CryptsyBase(object):
    def __init__(self):
        '''
        Can't get servertimezone via public API so hardcode to EST
        '''
        self.timezone = pytz.timezone(u'EST')

    def _get_info(self):
        raise NotImplementedError

    def _get_timezone(self):
        """
        Cryptsy seems to return all its timestamps in Eastern Standard Time,
        instead of doing the sane thing and returning UTC. But, the API does
        not make this a guarantee, so we do a request for getinfo and get the
        timezone then. We'll cache it, too.
        """
        if self.timezone is None:
            self.timezone = pytz.timezone(self._get_info()['servertimezone'])

        return self.timezone

    def _convert_timestamp(self, time_str):
        """
        Convert cryptsy timestamp to timezone-aware datetime object in UTC
        """
        naive_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        cryptsy_time = self._get_timezone()
        aware_time = cryptsy_time.normalize(cryptsy_time.localize(naive_time)).astimezone(pytz.utc)
        return aware_time

    @staticmethod
    def fix_json_types(node):
        '''
        As Crypts provides every (?) json value as unicode string,
        this takes a json dict and converts all floats to Decimal and ints to int
        '''
        if isinstance(node, dict):
            for key, item in node.items():
                node[key] = CryptsyBase.fix_json_types(item)
            return node
        elif isinstance(node, list):
            for index, item in enumerate(node):
                node[index] = CryptsyBase.fix_json_types(item)
            return node
        elif isinstance(node, unicode):
            try:
                node = Decimal(node)
                if node == node.to_integral_value():
                    node = int(node)
            except InvalidOperation, e:
                pass
            return node
        else:
            return node


class CryptsyPublic(CryptsyBase, SingleEndpoint):
    API_ENDPOINT = 'http://pubapi.cryptsy.com/api.php'

    def perform_get_request(self, method='', params={}):
        return self.fix_json_types(super(CryptsyPublic, self).perform_get_request(method, params))

    def get_market_data(self, market_id=None):
        '''
        General Market Data
        '''
        if market_id:
            params = {'method': 'singlemarketdata',
                    'marketid': market_id}
        else:
            params = {'method': 'marketdatav2'}

        market_data = []
        for crap, market in self.perform_get_request(params=params)['markets'].iteritems():
            market['lasttradetime'] = self._convert_timestamp(market['lasttradetime'])
            for trade in market['recenttrades']:
                trade['time'] = self._convert_timestamp(trade['time'])
            market_data.append(market)
        return market_data


    def get_order_data(self, market_id=None):
        '''
        General Orderbook Data
        '''
        if market_id:
            params = {'method': 'singleorderdata',
                    'marketid': market_id}
        else:
            params = {'method': 'orderdata'}
        return self.perform_get_request(params=params)


class Cryptsy(CryptsyBase, Exchange, SignedSingleEndpoint):
    API_ENDPOINT = 'https://www.cryptsy.com/api'
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.timezone = None
        self.market_currency_map = None
        self.pair_market_map = None

    def perform_request(self, method, data={}):
        return self.fix_json_types(super(Cryptsy, self).perform_request(method, data))

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
