import requests
import time

def get_all_markets():
    r = requests.get('http://pubapi.cryptsy.com/api.php?method=marketdatav2')
    print r.headers
    try:
        content = r.json()
        markets = content['return']['markets']
        return {label: Market(m) for label, m in markets.iteritems()}
    except:
        print r.text
    return {}

class Market:
    def __init__(self, raw_data):
        self.label = raw_data['label']
        self.trades = set([Market.format_trade(t) for t in raw_data['recenttrades']])

    @staticmethod
    def format_trade(trade):
        return (trade['time'], trade['price'])

    @staticmethod
    def trade_diff(old, new):
        #print "OLD"
        #print old.trades
        #print "NEW"
        #print new.trades
        return new.trades - old.trades

def trade_stream():
    old_markets = get_all_markets()
    for label, m in old_markets.iteritems():
        for trade in m.trades:
            yield (label, trade)

    #while True:
    for i in xrange(10):
        print "Request %d" % i
        new_markets = get_all_markets()
        for label in new_markets:
            if label in old_markets:
                trades = Market.trade_diff(old_markets[label], 
                    new_markets[label])
            else:
                trades = new_markets[label].trades

            for t in trades:
                yield (label, t)
        old_markets = new_markets
        time.sleep(10) 
