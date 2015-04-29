from __future__ import absolute_import
import pytest
from ..siren import SirenBuilder, SirenEntity, SirenAction, SirenLink

unit_test = pytest.mark.unit_test

@unit_test
def test_from_api_response():
    """Test the construction of objects from a json string."""
    json = """
    {
      "links": [
        {
          "href": "/resources?url=http://slashdot.org",
          "rel": [
            "self", "double-self"
          ]
        },
        {
          "href": "/views/5e88ecafcfe0520766cede7ef76dc16b2d869f5f6ce37141fde4224780a839c5dac26014336a22fabcf475873a5d254245e954fd9646e84c8e6ab087934eb873",
          "rel": [
            "view"
          ]
        }
      ],
      "class": [
        "Resource"
      ],
      "actions": [
        {
          "name": "get_with_url",
          "title": "get resource with url",
          "fields": [
            {
              "type": "text",
              "name": "url"
            }
          ],
          "href": "/resources",
          "type": "application/json",
          "method": "GET"
        }
      ],
      "properties": {
        "url": "http://slashdot.org",
        "time_fetched": 1409067477,
        "view_id": "5e88ecafcfe0520766cede7ef76dc16b2d869f5f6ce37141fde4224780a839c5dac26014336a22fabcf475873a5d254245e954fd9646e84c8e6ab087934eb873",
        "body_hash": "a3bf7ed65f40731cc33eb806476f3810883fc609b7dab609802fc844aaf06a4ec1836c0b21969acabe3c66b7d5dbd75fa664efad355eaf67d1055aa388f8b989"
      }
    }"""

    sb = SirenBuilder()
    sb.verify = False
    sb.request_factory = None
    so = sb.from_api_response(json)
    assert 'Resource' in so.classnames
    assert so.properties['url']
    assert so.properties['time_fetched']
    assert so.properties['view_id']
    assert so.properties['body_hash']

    links = so.links
    assert links and len(links) == 2
    assert so.get_link('self').href == '/resources?url=http://slashdot.org'
    assert so.get_link('double-self').href == '/resources?url=http://slashdot.org'
    assert so.get_link('view').href == '/views/5e88ecafcfe0520766cede7ef76dc16b2d869f5f6ce37141fde4224780a839c5dac26014336a22fabcf475873a5d254245e954fd9646e84c8e6ab087934eb873'

    actions = so.actions
    assert actions and len(actions) == 1

    action = actions[0]
    assert action.name
    assert action.href
    assert action.type
    assert action.method

    fields = action.fields
    assert fields and len(fields) == 1

    for f in fields:
        assert f['name']
        assert f['type']


def test_as_python_object():
    """Integration test of using hard-coded siren to create the hypermedia rest-client. This will attempt to contact the url."""
    base_url = 'http://127.0.0.1:5000/codex/views'
    classnames = ['view']
    properties = {'view_id': '1', 'url': 'http://slashdot.org', 'time_fetched': '1409067477'}
    actions = [SirenAction(name='update-view',
                           href='{}/1/'.format(base_url),
                           type='application/json',
                           fields=[{'type': 'text', 'name': 'url'}, {"type": "text","name": "time_fetched"},],
                           title=None,
                           method='PUT'),
               SirenAction(name='create-view',
                           href=base_url,
                           type='application/json',
                           fields=[{'type': 'text', 'name': 'url'}, {"type": "text", "name": "time_fetched"},],
                           title=None,
                           method='POST'),]
    links = [SirenLink(rel=['self'], href='http://127.0.0.1/views/1')]
    so = SirenEntity(classnames=classnames, properties=properties, actions=actions, links=links)

    view = so.as_python_object()
    assert type(view).__name__ == 'view'
    assert view.view_id == '1'
    assert view.url == 'http://slashdot.org'
    assert view.time_fetched == '1409067477'
    view.update_view(url='blank', time_fetched='2014-08-26 14:05:26', body='<html>TEST</html>')
