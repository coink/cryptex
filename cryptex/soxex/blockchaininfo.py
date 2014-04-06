from cryptex.soxex.wsconsumer import WebSocketConsumer
from cryptex.soxex.socketserver import WebSocketBase

from pprint import pprint

class BlockChainInfoSocket(WebSocketBase, WebSocketConsumer):
    WEBSOCKET_HOST = 'ws://ws.blockchain.info/inv'

    def __init__(self):
        super(BlockChainInfoSocket, self).__init__()

    def connect(self):
        self.start_socket(self.WEBSOCKET_HOST)

    def subscribe_txs(self):
        if self.socket is None:
            self.connect()
            self.message_callback = self.on_message

        self.send_message('{"op":"unconfirmed_sub"}')

    def subscribe_address(self, addr):
        if self.socket is None:
            self.connect()
            self.message_callback = self.on_message

        self.send_message('{"op":"addr_sub", "addr":"%s"}' % addr)

    def on_message(self, data):
        pass
