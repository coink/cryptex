import decimal

decimal.DefaultContext.rounding = decimal.ROUND_DOWN
decimal.DefaultContext.traps = decimal.ExtendedContext.traps.copy()
decimal.DefaultContext.traps[decimal.InvalidOperation] = 1
decimal.setcontext(decimal.DefaultContext)

DECIMAL_PRECISION = decimal.Decimal(10) ** -8

def quantize(decimal_value):
	return decimal_value.quantize(DECIMAL_PRECISION)
