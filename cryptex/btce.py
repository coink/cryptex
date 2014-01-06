import datetime

import pytz

from cryptex.exchange import Exchange
from cryptex.trade import Trade
from cryptex.order import Order
from cryptex.signed_single_endpoint import SignedSingleEndpoint
from cryptex.exception import APIException

class BTCE(Exchange, SignedSingleEndpoint):
    API_ENDPOINT = 'https://btc-e.com/tapi'
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
    
    def perform_request(self, method, data={}):
        try:
            return super(BTCE, self).perform_request(method, data)
        except APIException as e:
            if e.message == 'no orders':
                return {}
            else:
                raise e

    @staticmethod
    def _format_timestamp(timestamp):
        return pytz.utc.localize(datetime.datetime.utcfromtimestamp(
            timestamp))

    @staticmethod
    def _format_trade(trade_id, trade):
        if trade['type'] == 'buy':
            trade_type = Trade.BUY
        else:
            trade_type = Trade.SELL

        base, counter = trade['pair'].split('_')

        return Trade(
            trade_id = trade_id,
            trade_type = trade_type,
            base_currency = base,
            counter_currency = counter,
            time = BTCE._format_timestamp(trade['timestamp']),
            order_id = trade['order_id'],
            amount = trade['amount'],
            price = trade['rate']
        )

    def get_my_trades(self):
        trades = self.perform_request('TradeHistory')
        return [BTCE._format_trade(t_id, t) for t_id, t in trades.iteritems()]

    @staticmethod
    def _format_order(order_id, order):
        if order['type'] == 'buy':
            order_type = Trade.BUY
        else:
            order_type = Trade.SELL

        base, counter = order['pair'].split('_')

        return Order(
            order_id = order_id,
            order_type = order_type,
            base_currency = base,
            counter_currency = counter,
            time = BTCE._format_timestamp(order['timestamp_created']),
            amount = order['amount'],
            price = order['rate']
        )

    def get_my_open_orders(self):
        orders = self.perform_request('ActiveOrders')
        return [BTCE._format_order(o_id, o) for o_id, o in orders.iteritems()]

    def cancel_order(self, order_id):
        self.perform_request('CancelOrder', {'order_id': order_id})
        return None

    def get_markets(self):
        """
        BTC-e doesn't seem to expose its list of markets via its API. It's all 
        reluctantly hard-coded here.
        """
        return [
            ('BTC', 'USD'),
            ('BTC', 'RUR'),
            ('BTC', 'EUR'),

            ('LTC', 'BTC'),
            ('LTC', 'USD'),
            ('LTC', 'RUR'),
            ('LTC', 'EUR'),

            ('NMC', 'BTC'),
            ('NMC', 'USD'),

            ('NVC', 'BTC'),
            ('NVC', 'USD'),

            ('USD', 'RUR'),

            ('EUR', 'USD'),

            ('TRC', 'BTC'),

            ('PPC', 'BTC'),
            ('PPC', 'USD'),

            ('FTC', 'BTC'),

            ('XPM', 'BTC'),
        ]

    def _create_order(self, market, order_type, quantity, price):
        params = {
            'pair': market[0].lower() + '_' + market[1].lower(),
            'type': order_type,
            'amount': quantity,
            'rate': price
        }
        return self.perform_request('Trade', params)

    def buy(self, market, quantity, price):
        response = self._create_order(market, 'buy', quantity, price)
        return response['order_id']

    def sell(self, market, quantity, price):
        response = self._create_order(market, 'sell', quantity, price)
        return response['order_id']
