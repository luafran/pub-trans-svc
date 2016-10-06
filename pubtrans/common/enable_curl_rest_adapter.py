"""
This enables CURL for the asynchronous REST Adapter
"""
from tornado import httpclient

PROXY = {}
try:
    # Remember that pycurl needs the libcurl dev packages of your distro
    import pycurl  # pylint: disable=wrong-import-position
    assert pycurl

    import os  # pylint: disable=wrong-import-position, wrong-import-order
    from six.moves.urllib.parse import urlparse  # pylint: disable=wrong-import-position, wrong-import-order

    PROXY_ENV = os.environ.get('http_proxy')
    if PROXY_ENV:
        PARSED_PROXY = urlparse(PROXY_ENV)
        PROXY = {
            'proxy_host': PARSED_PROXY.hostname,
            'proxy_port': PARSED_PROXY.port
        }

    httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
except ImportError:
    pass
