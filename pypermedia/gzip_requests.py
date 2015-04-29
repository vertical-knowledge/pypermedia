__author__ = 'alexmaskovyak'

from requests import Request
import zlib


class GzipRequest(Request):
    """Encapsulates gzip requests. Currently just adds a header but may be extended in the future to do more."""
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        :param args: all of request's normal positional arguments, unused by GzipRequest itself
        :param kwargs: all of request's normal kwargs, unused by GzipRequest itself
        """
        super(GzipRequest, self).__init__(*args, **kwargs)  # delegate up

        # add acceptance of gzip
        self.headers['Accept-Encoding'] = 'gzip, deflate'  # always specify this since the requests library implicitly understands compression we might as well always request/use it

    def prepare(self):
        """
        Constructs a prepared request and compresses its contents.
        :return: prepared request with compressed payload
        :rtype: requests.PreparedRequest
        """
        p = super(GzipRequest, self).prepare()  # delegate up

        # modify payload when present
        if p.body and (self.method == 'POST' or self.method == 'PUT' or self.method == 'PATCH'):
            p.method = p.method.encode('utf-8')  # we have a byte-based message-body so we need bytes in the message header, harmless if already encoded properly

            # modify body and update headers
            p.body = self.gzip_compress(p.body)
            p.headers['Content-Length'] = len(p.body)
            p.headers['Content-Encoding'] = 'gzip'
        return p

    @staticmethod
    def gzip_compress(data):
        """
        Gzip compresses the data.

        :param data: data to compress
        :type data: str
        :return: compressed data
        :rtype: str
        """
        gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        return gzip_compress.compress(data) + gzip_compress.flush()
