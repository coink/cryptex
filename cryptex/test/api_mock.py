import os
import io

import httpretty

class APIMock():
    """
    Responses should be a {method: filename} map
    """
    def __init__(self, mock_url, mock_dir, responses):
        self.mock_url = mock_url
        self.responses = responses
        self.mock_dir = mock_dir

    def request_callback(self, request, uri, headers):
        method = request.parsed_body[u'method'][0]
        filename = self.responses[method]
        with io.open(os.path.join(self.mock_dir, filename), 'r') as f:
            contents = f.read()
        return (200, headers, contents)

    def __enter__(self):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST, self.mock_url,
                               body=self.request_callback)

    def __exit__(self, type, value, traceback):
        httpretty.disable()
        httpretty.reset()
