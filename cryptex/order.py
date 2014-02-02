class Order(object):
    def __init__(self, order_id, order_type, base_currency, counter_currency,
        time, amount, price):
        self.order_id = order_id
        self.order_type = order_type
        self.base_currency = base_currency
        self.counter_currency = counter_currency
        self.time = time
        self.amount = amount
        self.price = price

    def __str__(self):
        return repr(self.__dict__)
