# Soxex

Soxex creates an abstraction layer to many major exchange and ticker services
with websocket API's, including [blockchain.info](http://blockchain.info),
[BitStamp](http://bitstamp.net), and [Cryptsy](http://cryptsy.com).

## Dependencies

    pip install git+https://github.com/ekulyk/PythonPusherClient
    pip install websocket-client

## Installation

    pip install git+https://github.com/sjdev/cryptex.git

## Usage

Because each service offers a different set of API's, I have listed the
functionality of each below.

Service|subscribe\_txs|subscribe\_address|subscribe\_ticker
-------|--------------|------------------|-----------------
blockchain.info|YES|YES|NO|
BitStamp|YES|NO|NO|
Cryptsy|YES|NO|YES|

In services where it is supported, there are also unsubscribe\_\* functions so
that you do not need to completely close the connection in order to cut
a message stream off. Otherwise, all interfaces offer a close() method that
will completely terminate the connection.

The API interfaces can be used as follows:

### blockchain.info

    from cryptex.soxex.blockchaininfo import BlockChainInfoSocket

    def on_message(data):
        print data

    socket = BlockChainInfoSocket()
    socket.callback = on_message
    socket.subscribe_txs()
    socket.subscribe_address('XXX')

### BitStamp

    from cryptex.soxex.bitstamp import BitStampSocket

    def on_message(data):
        print data

    socket = BitStampSocket()
    socket.callback = on_message
    socket.subscribe_txs()

### Cryptsy

    from cryptex.soxex.cryptsy import CryptsySocket

    def on_message(data):
        print data

    socket = CryptsySocket()
    socket.callback = on_message
    socket.subscribe_txs()
    socket.subscribe_ticker()
