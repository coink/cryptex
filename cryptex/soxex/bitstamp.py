from cryptex.soxex.pushersocket import PusherClientInterface
from cryptex.soxex.socketserver import WebSocketBase

from pprint import pprint

class BitstampSocket(WebSocketBase, PusherClientInterface):
    PUSHER_APP_KEY = 'de504dc5763aeef9ff52'
    PUSHER_CHANNEL = 'live_trades'
    PUSHER_EVENT = 'trade'

    def __init__(self):
        pass

    def start(self):
        def callback(data):
            pprint(data)

        self.open_connection(self.PUSHER_APP_KEY, self.PUSHER_CHANNEL, self.PUSHER_EVENT, callback)

    def stop(self):
        self.close_connection()

