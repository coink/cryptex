class Trade(object):
    BUY = 0
    SELL = 1
    def __init__(self, trade_id, trade_type, base_currency, counter_currency,
        time, order_id, amount, price, fee=None):
        self.trade_id = trade_id
        self.trade_type = trade_type
        self.base_currency = base_currency
        self.counter_currency = counter_currency
        self.time = time
        self.order_id = order_id
        self.amount = amount
        self.price = price
        self.fee = fee

    def __str__(self):
        if self.trade_type == 0:
            ts = 'Buy'
        else:
            ts ='Sell'
        return '<%s of %.8f %s>' % (ts, self.amount, self.base_currency)
