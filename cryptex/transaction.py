class Transaction(object):
    '''
    Transaction that is neither deopsit nor withdrawal
    Used for CryptsyPoint credit
    '''
    transaction_type = 0
    def __init__(self, transaction_id, datetime, currency, amount, address, fee=None):
        self.transaction_id = transaction_id
        self.datetime = datetime
        self.currency = currency
        self.amount = amount
        self.address = address
        self.fee = fee
    
    def type(self):
        return self.__class__.__name__

    def __str__(self):
        return '<%s transaction of %.8f %s>' % (self.type(),
                                                self.amount,
                                                self.currency)
class Deposit(Transaction):
    transaction_type = 1

class Withdrawal(Transaction):
    transaction_type = 2
