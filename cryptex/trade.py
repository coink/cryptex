class Trade(object):
    BUY = 0
    SELL = 1
    def __init__(self, trade_id, trade_type, primary_curr, secondary_curr, 
        time, order_id, amount, price, fee=None):
        self.trade_id = trade_id
        self.trade_type = trade_type
        self.primary_curr = primary_curr
        self.secondary_curr = secondary_curr
        self.time = time
        self.order_id = order_id
        self.amount = amount
        self.price = price
        self.fee = fee
