from pubtrans.common import constants


class Context(object):  # pylint: disable=too-few-public-methods
    """
    Holds request information to be used by different components during request processing
    """

    def __init__(self, request=None, support=None):
        """
        Constructor
        """
        self.support = support
        self.request_id = None
        self.remote_ip = None

        if request:
            self.request_id = request.headers.get(
                constants.REQUEST_ID_HTTP_HEADER)

            self.remote_ip = request.headers.get('X-Forwarded-For',
                                                 request.headers.get('X-Real-Ip', '127.0.0.1'))
