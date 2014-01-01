import datetime

import pytz

from exchanges.exchange import Exchange
from exchanges.trade import Trade
from exchanges.order import Order
from exchanges.signed_single_endpoint import SignedSingleEndpoint
from exchanges.exception import APIException

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
                return []
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

        primary, secondary = trade['pair'].split('_')

        return Trade(
            trade_id = trade_id,
            trade_type = trade_type,
            primary_curr = primary,
            secondary_curr = secondary,
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

        primary, secondary = order['pair'].split('_')

        return Order(
            order_id = order_id,
            order_type = order_type,
            primary_curr = primary,
            secondary_curr = secondary,
            time = BTCE._format_timestamp(order['timestamp_created']),
            amount = order['amount'],
            price = order['rate']
        )

    def get_my_open_orders(self):
        orders = self.perform_request('ActiveOrders')
        return [BTCE._format_order(o_id, o) for o_id, o in orders.iteritems()]
