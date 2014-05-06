from decimal import Decimal, InvalidOperation
from urlparse import urljoin

import requests

from cryptex.exchange.btce import BTCEUtil

class BTCEPublic():
    """
    BTC-e public API https://btc-e.com/api/3/documentation
    All information is cached for 2 seconds on the server

    TODO: Add local caching to prevent frequent requests
    TODO: Format market pairs in output
    """
    URL_ROOT = "https://btc-e.com/api/3/"

    def __init__(self):
        self.markets = None
        self.lookup = None

    def perform_request(self, method, markets=[], limit=0, ignore_invalid=False):
        """
        Perform a request against the BTC-e public API. Market paris
        are represented as a list of tuples of the form ('BTC',
        'USD').
        """
        market_pair_strings = [BTCEUtil.market_to_pair(m) for m in markets]
        market_pair_component = "-".join(market_pair_strings)

        params = {}
        if limit:
            if limit > 2000:
                raise ValueError('Maximum limit is 2000')
            params['limit'] = limit

        if ignore_invalid:
            params['ignore_invalid'] = 1

        url = urljoin(BTCEPublic.URL_ROOT, method)
        if market_pair_component:
            url += "/" + market_pair_component
        #print url
        r = requests.get(url, params=params)
        return r.json(parse_float=Decimal)

    def get_info(self):
        """
        Information about currently active pairs, such as the maximum number of
        digits after the decimal point in the auction, the minimum price,
        maximum price, minimum quantity purchase / sale, hidden=1whether the
        pair and the pair commission.
        """
        j = self.perform_request('info')
        j['server_time'] = BTCEUtil.format_timestamp(j['server_time'])
        return j

    def get_ticker(self, markets, **kwargs):
        """
        Information about bidding on a pair, such as: the highest price, lowest
        price, average price, trading volume, trading volume in the currency of
        the last deal, the price of buying and selling.

        All information is provided in the last 24 hours.
        FIXME: What does that mean?
        """
        results = self.perform_request('ticker', markets, **kwargs)

        for (k, v) in results.iteritems():
            if isinstance(v, dict):
                v['updated'] = BTCEUtil.format_timestamp(v['updated'])

        return results

    def get_last_trade_prices(self):
        def to_tuple(pair):
            return tuple([s.upper() for s in pair.split('_')])

        pairs = self.get_info()['pairs']
        pairs = [to_tuple(p) for p in pairs]
        info = self.get_ticker(pairs)
        return {to_tuple(k): Decimal(v['last']) for k, v in info.iteritems()}

    def get_depth(self, market, limit=150):
        """
        Information on active warrants pair.
        Takes an optional parameter limit which indicates how many orders you
        want to display (default 150, max 2000)
        """
        return self.perform_request('depth', [market], limit=limit)

    def get_trades(self, market, limit=150):
        """
        Information on the latest deals. Takes an optional parameter limit
        which indicates how many orders you want to display (default 150, max
        2000).
        """
        response = self.perform_request('trades', [market], limit)

        for (market, trades) in response.iteritems():
            for t in trades:
                t['timestamp'] = BTCEUtil.format_timestamp(t['timestamp'])
        return response

    def get_markets(self):
        if self.markets is None:
            self.markets = [
                BTCEUtil.pair_to_market(pair)
                for pair in self.get_info()['pairs']
            ]

            flattened = set(y.lower() for x in self.markets for y in x)
            self.lookup = { k: {} for k in flattened }

            for pair in self.markets:
                self.lookup[pair[0].lower()][pair[1].lower()] = pair
                self.lookup[pair[1].lower()][pair[0].lower()] = pair

        return self.markets

    def market_with_currencies(self, currency_a, currency_b=None):
        if self.lookup is None:
            self.get_markets()

        if currency_b is None and currency_a in self.lookup.keys():
            return self.lookup[currency_a].values()

        if currency_a in self.lookup.keys() and currency_b in self.lookup[currency_a].keys():
            return self.lookup[currency_a][currency_b]

        return None
