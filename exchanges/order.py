class Order(object):
    def __init__(self, order_id, order_type, primary_curr, secondary_curr,
        time, amount, price):
        self.order_id = order_id
        self.order_type = order_type
        self.primary_curr = primary_curr
        self.secondary_curr = secondary_curr
        self.time = time
        self.amount = amount
        self.price = price
