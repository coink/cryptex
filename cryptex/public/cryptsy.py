from decimal import Decimal, InvalidOperation

from cryptex.exchange.cryptsy import CryptsyBase
from cryptex.exchange.single_endpoint import SingleEndpointAPI

class CryptsyPublic(CryptsyBase):

    def __init__(self):
        super(CryptsyPublic, self).__init__()
        self.api = SingleEndpointAPI('http://pubapi.cryptsy.com/api.php')

    def get_market_data(self, market_id=None):
        '''
        General Market Data
        '''
        params = {}
        if market_id:
            method = 'singlemarketdata'
            params = {'marketid': market_id}
        else:
            method = 'marketdatav2'

        market_data = {}
        for key, market in self.api.perform_request(method, params)['markets'].iteritems():
            if market['lasttradetime'] != '0000-00-00 00:00:00':
                market['lasttradetime'] = self._convert_datetime(market['lasttradetime'])
                for trade in market['recenttrades']:
                    trade['time'] = self._convert_datetime(trade['time'])
                market_data[key] = market
        return market_data

    def get_last_trade_prices(self):
        """
        Returns a dictionary of the form a: b, where a is
        a market tuple and b is the last trade price
        """
        market_data = self.get_market_data()
        trade_prices = {}
        for market_str, market in market_data.iteritems():
            market_tuple = tuple(market_str.split('/'))
            trade_prices[market_tuple] = Decimal(market['lasttradeprice'])
        return trade_prices

    def get_order_data(self, market_id=None):
        '''
        General Orderbook Data
        '''
        params = {}
        if market_id:
            method = 'singleorderdata'
            params = {'marketid': market_id}
        else:
            method = 'orderdata'
        return self.api.perform_request(method, params)

    def get_markets(self):
        return [tuple(m.split('/')) for m in self.get_market_data().keys()]


