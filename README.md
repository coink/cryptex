Cryptex: Cryptocurrency Exchange Client
=======================================

Python library that aims to provide a uniform access layer for cryptocurrency
exchanges.  Currently, the library supports access to [Cryptsy][1] and to
[BTC-e][2].

Installation
------------

    pip install git+https://github.com/coink/cryptex.git

Usage
-----

All methods are performed by first initializing an `Exchange` with your API key
and secret.

```python
>>> from cryptex.exchange import Cryptsy
>>> exchange = Cryptsy('API_KEY_HERE', 'API_SECRET_HERE')
```

Currently, the only exchanges are `cryptex.exchange.Cryptsy` and
`cryptex.exchange.BTCE`.

### Get available markets

```python
>>> exchange.get_markets()
[('BTC', 'USD'),
 ('BTC', 'RUR'),
 ('BTC', 'EUR'),
 ('LTC', 'BTC'),
 ('LTC', 'USD'),
 ('LTC', 'RUR'),
 ('LTC', 'EUR'),
 ('NMC', 'BTC'),
 ('NMC', 'USD'),
 ('NVC', 'BTC'),
 ('NVC', 'USD'),
 ('USD', 'RUR'),
 ('EUR', 'USD'),
 ('TRC', 'BTC'),
 ('PPC', 'BTC'),
 ('PPC', 'USD'),
 ('FTC', 'BTC'),
 ('XPM', 'BTC')]
```

Markets are represented throughout the library as tuples of the form
(`base_currency`, `counter_currency`).

### Get trade history

```python
>>> trades = exchange.get_my_trades()
>>> trades[0].__dict__
{'amount': Decimal('1.67577'),
 'base_currency': u'LTC',
 'counter_currency': u'BTC',
 'fee': None,
 'order_id': 12345,
 'price': Decimal('0.03505'),
 'time': datetime.datetime(2013, 12, 12, 6, 39, 31, tzinfo=<UTC>),
 'trade_id': u'20292389',
 'trade_type': 0}
```

Timestamps are all normalized to be timezone-aware `datetime.datetime` objects
in UTC. Prices and amounts are represented as `decimal.Decimal`s, never
`float`s.  `Trade.trade_type` must be either `Trade.BUY` or `Trade.SELL`.

### Get open orders

```python
>>> orders = exchange.get_my_open_orders()
>>> orders[0].__dict__
{'amount': Decimal('0.10000000'),
 'base_currency': u'LTC',
 'counter_currency': u'BTC',
 'order_id': u'12345',
 'order_type': 0,
 'price': Decimal('0.02000000'),
 'time': datetime.datetime(2014, 1, 6, 5, 56, 14, tzinfo=<UTC>)}
```

### Cancel an order

```python
>>> order_id = '12345'
>>> exchange.cancel_order(order_id)
```

### Trade

```python
>>> market = ("LTC", "BTC")
>>> amount = "0.1"
>>> price = "0.02"
>>> exchange.buy(market, amount, price)
13423
>>> exchange.sell(market, amount, price)
13424
```

The `buy` and `sell` methods both return the `order_id` of the created order.

[1]: https://www.cryptsy.com/
[2]: https://btc-e.com/
