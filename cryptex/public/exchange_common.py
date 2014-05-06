
class PublicCommon(object):

    def __init__(self):
        super(PublicCommon, self).__init__()
        print('ding')
        self.markets = None
        self.market_lookup = None

    def _make_market_lookup(self):
        flattened = set(y.lower() for x in self.markets for y in x)
        self.market_lookup = { k: {} for k in flattened }

        for pair in self.markets:
            self.market_lookup[pair[0].lower()][pair[1].lower()] = pair
            self.market_lookup[pair[1].lower()][pair[0].lower()] = pair

    def get_markets(self):
        self._make_market_lookup()
        return self.markets

    def lookup_markets(self, currency_a, currency_b=None):
        if self.market_lookup is None:
            self.get_markets()

        if currency_b is None and currency_a in self.market_lookup.keys():
            return self.market_lookup[currency_a].values()

        if currency_a in self.market_lookup.keys() and currency_b in self.market_lookup[currency_a].keys():
            return self.market_lookup[currency_a][currency_b]

        return None
