from cryptex.soxex.pushersocket import PusherClientInterface
from cryptex.soxex.socketserver import WebSocketBase

from pprint import pprint

class BitstampSocket(WebSocketBase, PusherClientInterface):
    PUSHER_APP_KEY = 'de504dc5763aeef9ff52'
    PUSHER_CHANNEL = 'live_trades'
    PUSHER_EVENT = 'trade'

    def __init__(self):
        super(BitstampSocket, self).__init__()

    def subscribe_txs(self):
        def callback(data):
            pprint(data)

        self.connect(self.PUSHER_APP_KEY,
                     self.PUSHER_CHANNEL,
                     self.PUSHER_EVENT,
                     callback)

    def unsubscribe_txs(self):
        self.close()

