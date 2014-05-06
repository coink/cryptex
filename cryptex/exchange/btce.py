import datetime
import pytz
from urlparse import urljoin
from decimal import Decimal

import requests

from cryptex.exchange import Exchange
from cryptex.trade import Sell, Buy
from cryptex.order import SellOrder, BuyOrder
from cryptex.transaction import Transaction, Deposit, Withdrawal
from cryptex.exchange.single_endpoint import SingleEndpointAPI
from cryptex.exception import APIException

class BTCEUtil(object):
    @staticmethod
    def format_timestamp(timestamp):
        return pytz.utc.localize(datetime.datetime.utcfromtimestamp(
            timestamp))

    @staticmethod
    def pair_to_market(pair):
        return tuple([c.upper() for c in pair.split('_')])

    @staticmethod
    def market_to_pair(market):
        return '_'.join((market[0].lower(), market[1].lower()))

class BTCE(Exchange):

    def __init__(self, key, secret):
        self.public = BTCEPublic()
        self.api = SingleEndpointAPI('https://btc-e.com/tapi', key, secret)

    def perform_request(self, method, data={}):
        try:
            return self.api.perform_request(method, data)
        except APIException as e:
            if e.message == 'no orders':
                return {}
            else:
                raise e
    @staticmethod
    def _format_trade(trade_id, trade):
        base, counter = BTCEUtil.pair_to_market(trade['pair'])
        if trade['type'] == 'buy':
            trade_type = Buy
        else:
            trade_type = Sell

        return trade_type(
            trade_id = trade_id,
            base_currency = base.upper(),
            counter_currency = counter.upper(),
            datetime = BTCEUtil.format_timestamp(trade['timestamp']),
            order_id = trade['order_id'],
            amount = trade['amount'],
            price = trade['rate'],
        )

    def get_my_trades(self):
        trades = self.perform_request('TradeHistory')
        return [BTCE._format_trade(t_id, t) for t_id, t in trades.iteritems()]

    @staticmethod
    def _format_order(order_id, order):
        if order['type'] == 'buy':
            order_type = BuyOrder
        else:
            order_type = SellOrder

        base, counter = BTCEUtil.pair_to_market(order['pair'])

        return order_type(
            order_id = order_id,
            base_currency = base.upper(),
            counter_currency = counter.upper(),
            datetime = BTCEUtil.format_timestamp(order['timestamp_created']),
            amount = order['amount'],
            price = order['rate']
        )

    def get_my_open_orders(self):
        orders = self.perform_request('ActiveOrders')
        return [self._format_order(o_id, o) for o_id, o in orders.iteritems()]

    def cancel_order(self, order_id):
        self.perform_request('CancelOrder', {'order_id': order_id})
        return None

    def _create_order(self, market, order_type, quantity, price):
        params = {
            'pair': BTCEUtil.market_to_pair(market),
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

    def get_my_transactions(self, limit=1000):
        transactions = []
        for tid, t in self.perform_request('TransHistory', {'count': limit}).iteritems():
            if t['type'] == 1:
                # Assume no fees for deopsit
                transactions.append(Deposit(tid,
                                            BTCEUtil.format_timestamp(t['timestamp']),
                                            t['currency'],
                                            t['amount'],
                                            '',
                                            0
                                    ))
            elif t['type'] == 2:
                idx = t['desc'].find('address ')
                if idx:
                    address = t['desc'][idx+8:]
                else:
                    address = ''
                # Withdraw fees are not provided by BTC-e API
                transactions.append(Withdrawal(tid,
                                            BTCEUtil.format_timestamp(t['timestamp']),
                                            t['currency'],
                                            t['amount'],
                                            address
                                    ))
        return transactions

    def get_my_balances(self):
        funds = {}
        for key, value in self.perform_request('getInfo')['funds'].iteritems():
            funds[key.upper()] = value
        return funds
