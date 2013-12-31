import datetime
from decimal import Decimal

import pytz
import requests

from exchanges.exchange import Exchange
from exchanges.trade import Trade
from exchanges.signed_single_endpoint import SignedSingleEndpoint

class BTCE(Exchange, SignedSingleEndpoint):
    API_ENDPOINT = 'https://btc-e.com/tapi'
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    @staticmethod
    def _format_trade(trade_id, trade):
        if trade['type'] == 'buy':
            trade_type = Trade.BUY
        else:
            trade_type = Trade.SELL

        trade_time = pytz.utc.localize(datetime.datetime.utcfromtimestamp(
            trade['timestamp']))

        return Trade(
            trade_id = trade_id,
            trade_type = trade_type,
            primary_curr = None,
            secondary_curr = None,
            time = trade_time,
            order_id = trade['order_id'],
            amount = trade['amount'],
            price = trade['rate']
        )

    def get_my_trades(self):
        trades = self.perform_request('TradeHistory')
        f_trades = [BTCE._format_trade(t_id, t) for t_id, t in trades.iteritems()]
        return (trades, f_trades)
