import pusherclient as pusher
import json
import logging

from pprint import pprint

class PusherConnection(object):

    def __init__(self, key, channel, event, callback):
        self.channel_name = channel
        self.event = event
        self.key = key
        self.event = event
        self.callback = callback

        def json_proxy(data):
            self.callback(json.loads(data))

        def handle_connect(data):
            channel = self.socket.subscribe(self.channel_name)
            channel.bind(self.event, json_proxy)

        self.socket = pusher.Pusher(key, log_level=logging.ERROR)
        self.socket.connection.bind('pusher:connection_established', handle_connect)
        self.socket.connect()

    def disconnect(self):
        self.socket.disconnect()

class PusherClientInterface(object):

    def __init__(self):
        super(PusherClientInterface, self).__init__()
        self.channels = {}

    def connect(self, key, channel, event, callback):
        if channel in self.channels:
            self.close(channel)

        self.channels[channel] = PusherConnection(key, channel, event, callback)

    def close(self, channel=None):
        if channel is None:
            for channel in self.channels.values():
                channel.disconnect()

            self.channels = {}
        else:
            self.channels[channel].disconnect()
            self.channels.pop(channel)
