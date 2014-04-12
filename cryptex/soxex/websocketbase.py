class WebSocketBase(object):

    class WebSocketBaseMethodUnimplemented(ValueError):
        pass

    def __init__(self):
       super(WebSocketBase, self).__init__()

    def subscribe_txs(self, callback=None):
        raise WebSocketBaseMethodUnimplemented()

    def unsubscribe_txs(self):
        raise WebSocketBaseMethodUnimplemented()

    def subscribe_address(self, callback=None):
        raise WebSocketBaseMethodUnimplemented()

    def unsubscribe_address(self):
        raise WebSocketBaseMethodUnimplemented()

    def subscribe_ticker(self, callback=None):
        raise WebSocketBaseMethodUnimplemented()

    def unsubscribe_ticker(self):
        raise WebSocketBaseMethodUnimplemented()

