from cryptex.soxex.wsconsumer import WebSocketConsumer
from cryptex.soxex.websocketbase import WebSocketBase

from pprint import pprint

class BlockChainInfoSocket(WebSocketBase, WebSocketConsumer):
    WEBSOCKET_HOST = 'ws://ws.blockchain.info/inv'

    def __init__(self):
        super(BlockChainInfoSocket, self).__init__()
        self.callback = None

    def _connect(self):
        self.start_socket(self.WEBSOCKET_HOST)

    def close(self):
        self.stop_socket()

    def subscribe_txs(self, callback=None):
        if self.socket is None:
            self._connect()
            self.message_callback = self.on_message

        self.callback = callback
        self.send_message('{"op":"unconfirmed_sub"}')

    def subscribe_address(self, addr, callback=None):
        if self.socket is None:
            self._connect()
            self.message_callback = self.on_message

        self.callback = callback
        self.send_message('{"op":"addr_sub", "addr":"%s"}' % addr)

    def on_message(self, data):
        if self.callback is not None:
            self.callback(data['x'])
