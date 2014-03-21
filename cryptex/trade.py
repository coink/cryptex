import cryptex.common as common

class Trade(object):
    '''
    Basic trade
    '''
    trade_type = 0
    def __init__(self, trade_id, base_currency, counter_currency,
                datetime, order_id, amount, price, fee=None, fee_currency=None):
        ''''
        :param trade_id: reference id on the exchange
        :param base_currency: the base currency of the trade (LTC in "LTC/BTC")
        :param counter_currency: the counter currency of the trade (BTC in "LTC/BTC")
        :param datetime: date and time of the trade in UTC
        :param order_id: id of referencing order on the exchange
        :param amount: amount that was bought/sold
        :param price: price at which the trade was made
        :param fee: anmount of fee payed to the exchange
        :param fee_currency: the currency the fee was payed in (base_currency or counter_currency)
        '''
        self.trade_id = trade_id
        self.base_currency = base_currency
        self.counter_currency = counter_currency
        self.datetime = datetime
        self.order_id = order_id
        self.amount = amount
        self.price = price
        self.fee = fee
        self.fee_currency = fee_currency

    def __setattr__(self, name, value):
        if name == 'fee_currency' and self.fee and \
                value not in (self.base_currency, self.counter_currency):
            raise ValueError('Wrong fee_currency "%r"' % value)
        super(Trade, self).__setattr__(name, value)

    def type(self):
        return self.__class__.__name__

    def __str__(self):
        return '<%s of %.8f %s>' % (self.type(),
                                    self.amount,
                                    self.base_currency)


class Buy(Trade):
    trade_type = 1

    def netto_amount(self):
        if self.fee is not None:
            return common.quantize(self.amount - self.fee)
        return self.amount

    def netto_total(self):
        return common.quantize(self.amount * self.price)

class Sell(Trade):
    trade_type = 2

    def netto_amount(self):
        return self.amount

    def netto_total(self):
        if self.fee is not None:
            return common.quantize((self.amount * self.price) - self.fee)
        return common.quantize(self.amount * self.price)
