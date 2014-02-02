class Transaction(object):
	def __init__(self, transaction_id, datetime, currency, amount, address, fee=None):
		self.transaction_id = transaction_id
		self.datetime = datetime
		self.currency = currency
		self.amount = amount
		self.address = address
		self.fee = fee

	def __str__(self):
		return '<%s transaction of %.8f %s>' % (self.__class__.__name__,
												self.amount,
												self.currency)

class Deposit(Transaction):
	transaction_type = 0
class Withdraw(Transaction):
	transaction_type = 1
