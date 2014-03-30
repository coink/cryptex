class Order(object):
    '''
    Basic order
    '''
    order_type = 0
    def __init__(self, order_id, base_currency, counter_currency,
                datetime, amount, price):
        self.order_id = order_id
        self.base_currency = base_currency
        self.counter_currency = counter_currency
        self.datetime = datetime
        self.amount = amount
        self.price = price

    def type(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self.__dict__)

class BuyOrder(Order):
    order_type = 1

class SellOrder(Order):
    order_type = 2
