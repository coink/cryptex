import time
import hmac
from hashlib import sha512
from urllib import urlencode
from decimal import Decimal

import requests

from cryptex.exception import APIException

class SingleEndpointAPI(object):
    """
    BTC-e and Cryptsy both employ the same API auth scheme and format.  There 
    exists a single endpoint. Different actions are performed by passing a 
    "method" parameter.  All requests are POST. All reponses are json, 
    returing an object with keys "success" and "return" (if successful).
    """
    def __init__(self, base_url, key=None, secret=None):
        self.base_url = base_url
        self.authenticated = key and secret
        self.key = key
        self.secret = secret

    def get_request_params(self, method, data):
        payload = {'method': method}
        payload.update(data)
        headers = {}

        if self.authenticated:
            payload.update({'nonce': int(time.time())})
            signature = hmac.new(self.secret, urlencode(payload),
                sha512).hexdigest()

            headers = {
                'Sign': signature,
                'Key': self.key
            }

        return (payload, headers)

    def perform_request(self, method, data={}):
        payload, headers = self.get_request_params(method, data)
        if self.authenticated:
            r = requests.post(self.base_url, data=payload, headers=headers)
        else:
            r = requests.get(self.base_url, params=payload, headers=headers)

        content = r.json(parse_float=Decimal)

        # Cryptsy returns success as a string, BTC-e as a int
        if int(content['success']) != 1:
            raise APIException(content['error'])

        # Cryptsy's createorder response is stupidly broken
        if method == 'createorder':
            content['return'] = {
                'orderid': content['orderid'],
                'moreinfo': content['moreinfo']
            }
        return content['return']
