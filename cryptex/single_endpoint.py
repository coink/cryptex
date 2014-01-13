import time
import hmac
from hashlib import sha512
from urllib import urlencode
from urlparse import urljoin
from decimal import Decimal

import requests

from cryptex.exception import APIException

class SingleEndpoint(object):
    ''' Simple enpoint for performing any kind of get request '''
    def perform_get_request(self, method='', params={}):
        request_url = type(self).API_ENDPOINT
        if method:
            if not request_url.endswith('/'):
                request_url += '/'
            request_url = urljoin(request_url, method)
        r = requests.get(request_url, params=params)
        content = r.json(parse_float=Decimal)
        if not content:
            raise APIException('Empty response')

        if 'success' in content:
            if int(content['success']) == 0:
                raise APIException(content['error'])
        if 'return' in content:
            return content['return']
        else:
            return content

class SignedSingleEndpoint(object):
    """
    BTC-e and Cryptsy both employ the same API auth scheme and format.  There 
    exists a single endpoint. Different actions are performed by passing a 
    "method" parameter.  All requests are POST. All reponses are json, 
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

        # Cryptsy's createorder response is stupidly broken
        if method == 'createorder':
            content['return'] = {
                'orderid': content['orderid'],
                'moreinfo': content['moreinfo']
            }

        # Cryptsy returns success as a string, BTC-e as a int
        if int(content['success']) == 1:
            return content['return']
        else:
            raise APIException(content['error'])
