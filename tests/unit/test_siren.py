from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pypermedia.siren import _check_and_decode_response, SirenBuilder, UnexpectedStatusError, \
    MalformedSirenError, SirenLink, SirenEntity, SirenAction, TemplatedString, \
    _create_action_fn

from requests import Response, PreparedRequest

import json
import mock
import six
import types
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
        ent = SirenEntity(['blah'], [], rel=['myrel'])
        entity = SirenEntity(['builderah'], [], entities=[ent])
        resp = entity.get_entities('myrel')
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

    def test_create_python_method_name(self):
        original_expected = [
            ('original', 'original',),
            ('original func', 'originalfunc',),
            ('original-func', 'original_func',),
            ('%bd#$%#$)@c', 'bdc'),
        ]
        for original, expected in original_expected:
            actual = SirenEntity._create_python_method_name(original)
            self.assertEqual(actual, expected)

    def test_create_python_method_name_invalid(self):
        bad = ('#$%^#$%&', '', '09345asda',)
        for name in bad:
            self.assertRaises(ValueError, SirenEntity._create_python_method_name, name)


class TestSirenAction(unittest2.TestCase):
    def test_add_field(self):
        action = SirenAction('action', 'blah', 'application/json')
        self.assertEqual(action.fields, [])
        action.add_field('field')
        self.assertEqual(len(action.fields), 1)
        self.assertDictEqual(action.fields[0], dict(name='field', type=None, value=None))

    def test_get_fields_dict(self):
        action = SirenAction('action', 'blah', 'application/json',
                             fields=[dict(name='field', type=None, value='whocares')])
        field_dict = action.get_fields_as_dict()
        self.assertDictEqual(dict(field='whocares'), field_dict)

    def test_as_siren(self):
        action = SirenAction('action', 'blah', 'application/json')
        siren_action = action.as_siren()
        expected = {'href': u'blah', 'name': u'action', 'title': u'action',
                    'fields': [], 'type': u'application/json', 'method': u'GET'}
        self.assertDictEqual(siren_action, expected)

    def test_as_json(self):
        action = SirenAction('action', 'blah', 'application/json')
        siren_action = action.as_json()
        self.assertIsInstance(siren_action, six.string_types)

    def test_get_bound_href(self):
        action = SirenAction('action', 'blah', 'application/json')
        bound_href, request_fields = action._get_bound_href(TemplatedString, x=1, y=2)
        self.assertEqual(bound_href, 'blah')
        self.assertDictEqual(request_fields, dict(x=1, y=2))

    def test_get_bound_href_with_template(self):
        action = SirenAction('action', 'http://host.com/{id}/{id}', 'application/json')
        bound_href, request_fields = action._get_bound_href(TemplatedString, x=1, y=2, id=3)
        self.assertEqual(bound_href, 'http://host.com/3/3')
        self.assertDictEqual(dict(x=1, y=2), request_fields)

    def test_get_bound_href_unboud_variables(self):
        action = SirenAction('action', 'http://host.com/{id}/{id}', 'application/json')
        self.assertRaises(ValueError, action._get_bound_href, TemplatedString, x=1, y=2)

    def test_as_request_get(self):
        action = SirenAction('action', 'http://blah.com', 'application/json')
        resp = action.as_request(x=1, y=2)
        self.assertIsInstance(resp, PreparedRequest)
        self.assertEqual(resp.method, 'GET')
        self.assertIn('y=2', resp.path_url)
        self.assertIn('x=1', resp.path_url)

    def test_as_request_post(self):
        action = SirenAction('action', 'http://blah.com', 'application/json', method='POST')
        resp = action.as_request(x=1, y=2)
        self.assertIsInstance(resp, PreparedRequest)
        self.assertEqual(resp.method, 'POST')
        self.assertEqual('/', resp.path_url)

    def test_as_request_delete(self):
        action = SirenAction('action', 'http://blah.com', 'application/json', method='DELETE')
        resp = action.as_request(x=1, y=2)
        self.assertIsInstance(resp, PreparedRequest)
        self.assertEqual(resp.method, 'DELETE')
        self.assertEqual('/', resp.path_url)

    def test_make_request(self):
        action = SirenAction('action', 'http://blah.com', 'application/json')
        mck = mock.Mock(send=mock.Mock(return_value=True))
        resp = action.make_request(_session=mck, x=1, y=2)
        self.assertTrue(resp)
        self.assertEqual(mck.send.call_count, 1)
        self.assertIsInstance(mck.send.call_args[0][0], PreparedRequest)


class TestSirenLink(unittest2.TestCase):
    def test_init_errors(self):
        self.assertRaises(ValueError, SirenLink, [], 'href')
        self.assertRaises(ValueError, SirenLink, None, 'href')
        self.assertRaises(ValueError, SirenLink, ['blah'], '')

    def test_init_rel_string(self):
        siren_link = SirenLink('blah', 'href')
        self.assertEqual(['blah'], siren_link.rel)

    def test_add_rel(self):
        link = SirenLink(['blah'], 'blah')
        self.assertListEqual(link.rel, ['blah'])
        link.add_rel('two')
        self.assertListEqual(['blah', 'two'], link.rel)
        link.add_rel('two')
        self.assertListEqual(['blah', 'two'], link.rel)

    def test_rem_rel(self):
        link = SirenLink(['blah'], 'blah')
        link.rem_rel('notreal')
        self.assertListEqual(link.rel, ['blah'])
        link.rem_rel('blah')
        self.assertListEqual(link.rel, [])

    def test_as_siren(self):
        link = SirenLink(['blah'], 'href')
        self.assertDictEqual(link.as_siren(), dict(rel=['blah'], href='href'))

    def test_as_json(self):
        link = SirenLink(['blah'], 'href')
        self.assertIsInstance(link.as_json(), six.string_types)

    def test_as_request(self):
        href = 'http://notreal.com/'
        link = SirenLink(['blah'], 'http://notreal.com')
        req = link.as_request()
        self.assertIsInstance(req, PreparedRequest)
        self.assertEqual(href, req.url)

    def test_make_request(self):
        link = SirenLink(['blah'], 'http://notreal.com')
        session = mock.MagicMock()
        resp = link.make_request(_session=session)
        self.assertEqual(session.send.call_count, 1)

    def test_as_python_object(self):
        """
        Mostly just an explosion test.
        """
        link = SirenLink('blah', 'blah')
        with mock.patch.object(link, 'make_request') as make_request:
            with mock.patch.object(link, 'from_api_response') as from_api_respons:
                resp = link.as_python_object()
                self.assertEqual(make_request.call_count, 1)
                self.assertEqual(from_api_respons.call_count, 1)


class TestTemplatedString(unittest2.TestCase):
    def test_init(self):
        base = '/blah/'
        template = TemplatedString(base)
        self.assertEqual(len(template.param_dict), 0)
        base = '/{id}/{pk}/sdf'
        template = TemplatedString(base)
        self.assertEqual(len(template.param_dict), 2)
        self.assertEqual(template.param_dict['id'], '{id}')
        self.assertEqual(template.param_dict['pk'], '{pk}')

    def test_items(self):
        base = '/{id}/{pk}/sdf'
        template = TemplatedString(base)
        for p in [('id', '{id}'), ('pk', '{pk}')]:
            self.assertIn(p, template.items())

    def test_unbound_variables(self):
        base = '/{id}/{pk}/sdf'
        template = TemplatedString(base)
        for p in ['id', 'pk']:
            self.assertIn(p, template.unbound_variables())

    def test_bind(self):
        base = '/{id}/{pk}/sdf'
        template = TemplatedString(base)
        template2 = template.bind(id=1)
        self.assertEqual(template2.base, '/1/{pk}/sdf')
        self.assertDictEqual(template2.param_dict, {'pk': '{pk}'})

        template3 = template2.bind(id=1)
        self.assertEqual(template3.base, '/1/{pk}/sdf')
        self.assertDictEqual(template3.param_dict, {'pk': '{pk}'})

        template4 = template3.bind(pk=2)
        self.assertEqual(template4.base, '/1/2/sdf')
        self.assertDictEqual(template4.param_dict, {})

        template5 = template4.bind(who='asdknf', cares=23)
        self.assertEqual(template5.base, '/1/2/sdf')
        self.assertDictEqual(template5.param_dict, {})

    def test_has_unbound_variables(self):
        base = '/{id}/{pk}/sdf'
        template = TemplatedString(base)
        self.assertTrue(template.has_unbound_variables())

        base = '/sdf'
        template = TemplatedString(base)
        self.assertFalse(template.has_unbound_variables())

    def test_as_string(self):
        base = '/{id}/{pk}/sdf'
        template = TemplatedString(base)
        self.assertEqual(base, template.as_string())


class TestMiscellaneousSiren(unittest2.TestCase):
    def test_create_action_function(self):
        action = mock.MagicMock()
        siren = mock.MagicMock()
        func = _create_action_fn(action, siren)
        self.assertIsInstance(func, types.FunctionType)
        slf = mock.MagicMock()
        resp = func(slf, blah='ha')
        self.assertEqual(siren.from_api_response.return_value.as_python_object.return_value, resp)
        self.assertEqual(action.make_request.return_value, siren.from_api_response.call_args[1]['response'])

    def test_create_action_function_none_response(self):
        action = mock.MagicMock()
        siren = mock.MagicMock()
        siren.from_api_response.return_value = None
        func = _create_action_fn(action, siren)
        slf = mock.MagicMock()
        resp = func(slf, blah='ha')
        self.assertIsNone(resp)

