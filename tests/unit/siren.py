from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pypermedia.siren import _check_and_decode_response, SirenBuilder, UnexpectedStatusError, \
    MalformedSirenError, SirenLink, SirenEntity

from requests import Response

import json
import mock
import six
import unittest2


class TestSirenBuilder(unittest2.TestCase):
    def test_check_and_decode_response_404(self):
        """
        Tests the private _check_and_decode_response method
        """
        resp = mock.Mock(status_code=404)
        self.assertIsNone(_check_and_decode_response(resp))

    def test_check_and_decode_bad_status_code(self):
        """
        Tests that an exception is raised for non-200
        status codes.
        """
        resp = mock.Mock(status_code=400)
        self.assertRaises(UnexpectedStatusError, _check_and_decode_response, resp)

    def test_check_and_decode_empty_text(self):
        """
        Tests that an exception is raised when
        the body is empty.
        """
        resp = mock.Mock(status_code=200, text='')
        self.assertRaises(MalformedSirenError, _check_and_decode_response, resp)

    def test_construct_link(self):
        builder = SirenBuilder()
        link = builder._construct_link(dict(rel=['rel'], href='whocares'))
        self.assertIsInstance(link, SirenLink)

    def test_construct_link_bad(self):
        """
        Tests constructing a link.
        """
        builder = SirenBuilder()
        self.assertRaises(KeyError, builder._construct_link, dict(rel=['blah']))

    def test_construct_entity_missing_class(self):
        entity = dict(properties={}, actions=[], links=[], entities=[])
        builder = SirenBuilder()
        self.assertRaises(KeyError, builder._construct_entity, entity)

    def test_construct_entity_missing_non_essential(self):
        """Tests that non-essential pieces are ignored."""
        entity = {'class': ['blah']}
        builder = SirenBuilder()
        resp = builder._construct_entity(entity)
        self.assertIsInstance(resp, SirenEntity)

    def test_from_api_response(self):
        """
        Tests for a requests.Response object.
        """
        entity = {'class': ['blah']}
        resp = Response()
        resp.status_code = 200
        resp._content = six.binary_type(json.dumps(entity).encode('utf8'))
        builder = SirenBuilder()
        siren = builder.from_api_response(resp)
        self.assertIsInstance(siren, SirenEntity)

    def test_bad_text_from_api_response(self):
        builder = SirenBuilder()
        self.assertRaises(MalformedSirenError, builder.from_api_response, 'asdfgsjdfg')

    def test_from_api_response_bad_type(self):
        builder = SirenBuilder()
        self.assertRaises(TypeError, builder.from_api_response, [])


class TestSirenEntity(unittest2.TestCase):
    def test_init_no_classnames(self):
        self.assertRaises(ValueError, SirenEntity, None, None)
        self.assertRaises(ValueError, SirenEntity, [], None)

    def test_get_link_no_links(self):
        entity = SirenEntity(['blah'], None)
        self.assertIsNone(entity.get_links('sakdf'))

    def test_get_link(self):
        link = mock.Mock(rel=['myrel'])
        entity = SirenEntity(['blah'], [link])
        resp = entity.get_links('myrel')
        self.assertEqual([link], resp)
        self.assertListEqual(entity.get_links('badrel'), [])

    def test_get_entity_no_entities(self):
        entity = SirenEntity(['blah'], None)
        self.assertEqual(entity.get_entities('sakdf'), [])

    def test_get_entities(self):
        ent = mock.Mock(rel=['myrel'])
        entity = SirenEntity(['blah'], [ent])
        resp = entity.get_links('myrel')
        self.assertEqual([ent], resp)
        self.assertEqual(entity.get_entities('badrel'), [])

    def test_get_primary_classname(self):
        entity = SirenEntity(['blah'], None)
        self.assertEqual(entity.get_primary_classname(), 'blah')

    def test_get_base_classnames(self):
        entity = SirenEntity(['blah'], None)
        self.assertListEqual(entity.get_base_classnames(), [])
        entity = SirenEntity(['blah', 'second'], None)
        self.assertListEqual(entity.get_base_classnames(), ['second'])

    def test_as_siren(self):
        entity = SirenEntity(['blah'], [])
        siren_dict = entity.as_siren()
        self.assertIsInstance(siren_dict, dict)
        self.assertDictEqual(siren_dict, {'class': ['blah'], 'links': [], 'entities': [], 'actions': [], 'properties': {}})

    def test_as_json(self):
        entity = SirenEntity(['blah'], [])
        json_string = entity.as_json()
        self.assertIsInstance(json_string, six.string_types)

    def test_as_python_object(self):
        entity = SirenEntity(['blah'], [])
        siren_class = entity.as_python_object()
        self.assertTrue(hasattr(siren_class, 'get_entities'))
        # TODO we definitely need some more tests for this part.
