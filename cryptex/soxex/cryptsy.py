from cryptex.soxex.pushersocket import PusherClientInterface
from cryptex.soxex.socketserver import WebSocketBase

from pprint import pprint

class CryptsySocket(WebSocketBase, PusherClientInterface):
    PUSHER_APP_KEY = 'cb65d0a7a72cd94adf1f'
    PUSHER_CHANNEL_TRADE = 'trade.'
    PUSHER_CHANNEL_TICKER = 'ticker.'
    PUSHER_EVENT = 'message'

    def __init__(self):
        super(CryptsySocket, self).__init__()

    def stop(self):
        self.close_connection()

    def subscribe_txs(self, market_id):
        def callback(data):
            pprint(data)

        self.connect(self.PUSHER_APP_KEY,
                     self.PUSHER_CHANNEL_TRADE + market_id,
                     self.PUSHER_EVENT,
                     callback)

    def unsubscribe_txs(self, market_id):
        self.close(self.PUSHER_CHANNEL_TRADE + market_id)

    def subscribe_ticker(self, market_id):
        def callback(data):
            pprint(data)

        self.connect(self.PUSHER_APP_KEY,
                     self.PUSHER_CHANNEL_TICKER + market_id,
                     self.PUSHER_EVENT,
                     callback)

    def unsubscribe_ticker(self, market_id):
        self.close(self.PUSHER_CHANNEL_TICKER + market_id)

    def unsubscribe_all(self):
        self.close()
