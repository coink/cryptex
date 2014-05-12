from decimal import Decimal

from cryptex.transaction import Deposit, Withdrawal
from cryptex.trade import Buy, Sell
from functools import partial

class PLCalculator(object):
    def __init__(self, exchange):
        self.exchange = exchange

    @staticmethod
    def convert_transaction(market, tx):
        """
        Convert to buy orders or sell trades of 0 cost and 0 price
        """
        base, counter = market
        if isinstance(tx, Deposit):
            trade_cls = Buy
        else:
            trade_cls = Sell

        return trade_cls(None, base, counter, tx.datetime, None,
                         tx.amount, Decimal('0'))

    def _get_trades(self, market, trades, transactions):
        """
        Returns all trades in a particular market along with
        transaction of the base currency, sorted by time.
        """
        base, counter = market
        trades = [t for t in trades
                  if t.base_currency == base and 
                  t.counter_currency == counter]
        txs = [t for t in transactions
               if t.currency == base]
        tx_trades = map(partial(PLCalculator.convert_transaction, market), txs)

        all_trades = sorted(trades + tx_trades, key=lambda x: x.datetime)
        return all_trades

    def get_markets(self, trades):
        return set([(t.base_currency, t.counter_currency) for t in trades])

    @staticmethod
    def calculate_pl(market, trades):
        base, counter = market
        acc = []
        for trade in trades:
            if isinstance(trade, Buy):
                new_trade = Buy(None, base, counter, trade.datetime, None,
                                trade.amount, trade.price)
                acc.append(new_trade)
            else:
                oldest_buy = None
                total_amount = Decimal('0')
                while total_amount < trade.amount:
                    oldest_buy = acc.pop()
                    total_amount += oldest_buy.amount
                buy_amount = total_amount - trade.amount
                if buy_amount != Decimal('0'):
                    new_trade = Buy(None, base, counter, oldest_buy.datetime,
                                    None, buy_amount, oldest_buy.price) 
                    acc.append(new_trade)
        return acc

    def unrealized_pl(self, market=None):
        all_trades = self.exchange.get_my_trades()
        all_transactions = self.exchange.get_my_transactions()
        markets = self.get_markets(all_trades)

        result = {}
        for m in markets:
            trades = self._get_trades(m, all_trades, all_transactions)
            result[m] = PLCalculator.calculate_pl(m, trades)

        if market is None:
            return result
        else:
            try:
                return result[market]
            except KeyError:
                return [] 
