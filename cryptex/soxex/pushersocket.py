import pusherclient as pusher
import json
import logging

from pprint import pprint

class PusherClientInterface(object):

    def open_connection(self, key, channel, event, callback):
        self.pusher_channel = channel
        self.pusher_event = event
        self.pusher_key = key
        self.pusher_event = event
        self.pusher_callback = callback

        def json_proxy(data):
            self.pusher_callback(json.loads(data))

        def handle_connect(data):
            channel = socket.subscribe(self.pusher_channel)
            channel.bind(self.pusher_event, json_proxy)

        socket = pusher.Pusher(key, log_level=logging.ERROR)
        socket.connection.bind('pusher:connection_established', handle_connect)
        socket.connect()

    def close_connection(self):
        self.socket.disconnect()
