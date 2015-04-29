import requests
import requests.exceptions
import sys

from pypermedia.gzip_requests import GzipRequest
from pypermedia.siren import SirenBuilder


class HypermediaClient(object):
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


class ConnectError(Exception):
    """Standard error for an inability to connect to the server."""
    pass


class APIError(Exception):
    """Bucket for errors related to server responses."""
    pass