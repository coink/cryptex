import time
import hmac
from hashlib import sha512
from urllib import urlencode
from decimal import Decimal

import requests

class SignedSingleEndpoint(object):
    """
    BTC-e and Cryptsy both employ the same API auth scheme and format.  There 
    exists a single endpoint. Different actions are performed by passing a 
    "method" parameter.  All requests are PPOST. All reponses are json, 
    returing an object with keys "success" and "return" (if successful).
    """
    def get_request_params(self, method, data):
        payload = {
            'method': method,
            'nonce': int(time.time())
        }
        payload.update(data)
        signature = hmac.new(self.secret, urlencode(payload), 
            sha512).hexdigest()
        
        headers = {
            'Sign': signature, 
            'Key': self.key
        }
        return (payload, headers)

    def perform_request(self, method, data={}):
        payload, headers = self.get_request_params(method, data)
        r = requests.post(type(self).API_ENDPOINT, data=payload, headers=headers)
        content = r.json(parse_float=Decimal)
        return content['return']
