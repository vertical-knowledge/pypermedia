import datetime
import re
import requests
import requests.exceptions
import sys

from gzip_requests import GzipRequest
from hypermedia_objects import SirenBuilder


class CodexClient(object):
    """Entry-point and helper methods for using the codex service. This performs the initial setup, all other client calls are created dynamically from service responses."""

    @staticmethod
    def connect(root_url, verify=False, request_factory=GzipRequest):
        """
        Creates a client by connecting to the root api url. Pointing to other urls is possible so long as their responses correspond to standard siren-json.

        :param root_url: root api url
        :type root_url: str or unicode
        :param verify: whether to verify ssl certificates from the server or ignore them (should be false for local dev)
        :type verify: bool
        :param request_factory: constructor of request objects
        :type request_factory: type or function
        :return: codex client generated from root url
        :rtype: object
        """
        # connect to server and get json
        # convert to siren
        # get as python object
        try:
            request = request_factory('GET', root_url)
            p = request.prepare()
            response = requests.Session().send(p, verify=verify)
        except requests.exceptions.ConnectionError as e:
            # this is the deprecated form but it preserves the stack trace so let's use this
            # it's not like this is going to be a big problem when porting to Python 3 in the future
            exception = ConnectError('Unable to connect to server! Unable to construct client. root_url="{}" verify="{}"'.format(root_url, verify), e)
            raise ConnectError, exception, sys.exc_info()[2]

        if not response:
            raise ConnectError('No response received from server! Unable to construct client. root_url="{}" verify="{}"'.format(root_url, verify))

        if response.status_code != 200:
            raise ConnectError('Received unexpected status message from server. Received status="{}", expected=200. Unable to construct client. root_url="{}" verify="{}"'.format(
                response.status_code,
                root_url,
                verify))

        if not response.text:
            raise APIError('Empty response received. Expected siren-json response. Unable to construct client. root-url="{}" verify="{}"'.format(root_url, verify))

        siren_builder = SirenBuilder()
        siren_builder.verify = verify
        siren_builder.request_factory = request_factory
        siren = siren_builder.from_api_response(response=response)
        return siren.as_python_object()

    @staticmethod
    def create_view_dict(response, request=None, url=None, **metadata):
        """
        Creates a dictionary of expected parameters.

        :param response: response object
        :type response: requests.Response
        :param request: request object
        :type request: requests.Request
        :param url: url
        :type url: str
        :param metadata: dictionary of key/value metadata to assign to this view
        :type metadata: dict[str, str]
        :return: dictionary of parameters to send during the creation of a view
        :rtype: dict[str, str]
        """
        request = response.request if not request else request
        url = request.url if not url else url
        return {
            'url': url,
            'time_fetched': datetime.datetime.utcnow().isoformat(),

            'request_headers': dict(request.headers),
            'post_data': request.body,

            'response_headers': dict(response.headers),
            'status_code': response.status_code,
            'content': response.content.encode('hex') if response.content else response.content,
            'content_encoding': response.encoding,
            'metadata': dict(metadata)
        }


class ConnectError(Exception):
    """Standard error for an inability to connect to the server."""
    pass


class APIError(Exception):
    """Bucket for errors related to server responses."""
    pass


def sandbox():
    """
    Various one-time runs for experimental use.
    """
    from requests import Session
    from hypermedia_objects import GzipRequest, SirenAction

    # fields = {'url':'blah', 'time_fetched':'2014-11-11T15:47:34.062578', 'content': '1234abef49e0'}
    # req = GzipRequest('POST', 'https://app0.codex.vkdev/codex/views/', data=fields)
    # p = req.prepare()
    # Session().send(p, verify=False)


    codex_url = 'https://app0.codex.vkdev/codex/'
    urls = ['http://www.reddit.com/', 'http://slashdot.org', 'https://news.google.com/', ]
    responses = map(requests.get, urls)

    # connect to server
    codex = CodexClient.connect(codex_url, verify=False, request_factory=requests.Request)
    views = codex.views()

    import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # initialize logging for urllib output
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    # test creation and response
    for response in responses:
        original_fields = CodexClient.create_view_dict(response, origin='script')
        fields = SirenAction.prepare_payload_parameters(**original_fields)

        req = GzipRequest('POST', 'https://app0.codex.vkdev/codex/views/', data=fields)
        p = req.prepare()
        Session().send(p, verify=False)

        views.create(**original_fields)


# ======
# script
# ======

if __name__ == '__main__':
    print('no-op')
    sandbox()
