from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pypermedia.client import HypermediaClient, ConnectError

import mock
import requests
import unittest2


class TestClient(unittest2.TestCase):
    """
    This is kinda shit since it really
    needs to be integration tested.
    """

    def test_connect(self):
        builder = mock.MagicMock()
        request_factory = mock.MagicMock()
        session = mock.MagicMock()
        resp = HypermediaClient.connect('blah', session=session, request_factory=request_factory, builder=builder)
        self.assertEqual(builder.return_value.from_api_response.return_value.as_python_object.return_value, resp)

    def test_send_and_construct(self):
        builder = mock.MagicMock()
        request_factory = mock.MagicMock()
        session = mock.MagicMock()
        request = mock.Mock(url='url')
        resp = HypermediaClient.send_and_construct(request, session=session, request_factory=request_factory, builder=builder)
        self.assertEqual(builder.return_value.from_api_response.return_value.as_python_object.return_value, resp)

    def test_send_and_construct_error(self):
        request = mock.Mock(url='url')
        session = mock.Mock(send=mock.Mock(side_effect=requests.exceptions.ConnectionError))
        self.assertRaises(ConnectError, HypermediaClient.send_and_construct, request, session=session)
