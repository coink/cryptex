import websocket
import thread
import time
import json

from pprint import pprint

class WebSocketConsumer(object):

    def __init__(self):
        super(WebSocketConsumer, self).__init__()

        self.socket = None
        self.is_open = False
        self.backlog = []

    def start_socket(self, url):
        def on_message(ws, data):
            self.message_callback(json.loads(data))

        def on_error(ws, error):
            print '{} Error: {}'.format(type(self), error)

        def on_close(ws):
            pass

        def on_open(ws):
            print 'Connection established'
            self.is_open = True

            backlog = self.backlog
            self.backlog = []

            for msg in backlog:
                self.send_message(msg)

        def run():
            self.socket.run_forever()

        self.socket = websocket.WebSocketApp(url,
                                             on_message=on_message,
                                             on_error=on_error,
                                             on_close=on_close)
        self.socket.on_open = on_open

        thread.start_new_thread(run, ())

    def stop_socket(self):
        if self.socket is not None:
            self.socket.close()

    def send_message(self, message):
        if self.socket is not None and self.is_open:
            self.socket.send(message)
        else:
            self.backlog.append(message)
