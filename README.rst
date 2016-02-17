Hypermedia Client
=================



.. image:: https://travis-ci.org/vertical-knowledge/pypermedia.svg?branch=master&style=flat
    :target: https://travis-ci.org/vertical-knowledge/pypermedia
    :alt: test status

.. image:: https://coveralls.io/repos/vertical-knowledge/pypermedia/badge.svg?branch=master&style=flat
    :target: https://coveralls.io/r/vertical-knowledge/pypermedia?branch=master
    :alt: test coverage

.. image:: https://readthedocs.org/projects/pypermedia/badge/?version=latest
    :target: https://pypermedia.readthedocs.org/
    :alt: Documentation Status

..
    .. image:: https://pypip.in/version/pypermedia/badge.svg?style=flat
        :target: https://pypi.python.org/pypi/pypermedia/
        :alt: current version

..
    .. image:: https://pypip.in/download/pypermedia/badge.png?style=flat
        :target: https://pypi.python.org/pypi/pypermedia/
        :alt: PyPI downloads

.. image:: https://img.shields.io/pypi/dm/pypermedia.svg?style=flat
    :target: https://pypi.python.org/pypi/pypermedia/
    :alt: python versions


.. image:: https://img.shields.io/github/stars/vertical-knowledge/pypermedia.svg?style=flat
    :target: https://github.com/vertical-knowledge/pypermedia/
    :alt: stars



The Hypermedia client serves as a python developer's API for access to services
which return certain hypermedia mimetypes. The client self-discovers services 
from the endpoint and relies entirely upon responses from the server for 
operation. It can be considered a proxy for the REST service and allows 
developers to program against a hypermedia provider without need for 
understanding HTTP or network conceits aside from the root API URL. 

Currently supports SIREN.

SIREN
-----

For information on the protocol see the
`specification. <https://github.com/kevinswiber/siren>`_

The client allows you to interact with a SIREN protocol web api
as if it were a python object.  It automatically generates python
objects with attributes corresponding to the SIREN properties and
methods to the SIREN actions.  Additionally, it gives you access to
SIREN links and subentities.

To connect the client you simply need to provide an initial
url.

.. code-block:: python

    >>> from pypermedia import HypermediaClient
    >>> siren_obj = HypermediaClient('http://myapp.io/api/my_resource/')

Now suppose the endpoint returned the following SIREN response.

.. code-block:: javascript

    {
      "class": [ "order" ],
      "properties": {
          "orderNumber": 42,
          "itemCount": 3,
          "status": "pending"
      },
      "entities": [
        {
          "class": [ "items", "collection" ],
          "rel": [ "http://x.io/rels/order-items" ],
          "href": "http://api.x.io/orders/42/items"
        },
        {
          "class": [ "info", "customer" ],
          "rel": [ "http://x.io/rels/customer" ],
          "properties": {
            "customerId": "pj123",
            "name": "Peter Joseph"
          },
          "links": [
            { "rel": [ "self" ], "href": "http://api.x.io/customers/pj123" }
          ]
        }
      ],
      "actions": [
        {
          "name": "add-item",
          "title": "Add Item",
          "method": "POST",
          "href": "http://api.x.io/orders/42/items",
          "type": "application/x-www-form-urlencoded",
          "fields": [
            { "name": "orderNumber", "type": "number" },
            { "name": "productCode", "type": "text" },
            { "name": "quantity", "type": "number" }
          ]
        }
      ],
      "links": [
        { "rel": [ "self" ], "href": "http://api.x.io/orders/42" },
        { "rel": [ "previous" ], "href": "http://api.x.io/orders/41" },
        { "rel": [ "next" ], "href": "http://api.x.io/orders/43" }
      ]
    }

.. testsetup:: siren

    from pypermedia.siren import SirenBuilder

    response = {
      "class": [ "order" ],
      "properties": {
          "orderNumber": 42,
          "itemCount": 3,
          "status": "pending"
      },
      "entities": [
        {
          "class": [ "items", "collection" ],
          "rel": [ "http://x.io/rels/order-items" ],
          "href": "http://api.x.io/orders/42/items"
        },
        {
          "class": [ "info", "customer" ],
          "rel": [ "http://x.io/rels/customer" ],
          "properties": {
            "customerId": "pj123",
            "name": "Peter Joseph"
          },
          "links": [
            { "rel": [ "self" ], "href": "http://api.x.io/customers/pj123" }
          ]
        }
      ],
      "actions": [
        {
          "name": "add-item",
          "title": "Add Item",
          "method": "POST",
          "href": "http://api.x.io/orders/42/items",
          "type": "application/x-www-form-urlencoded",
          "fields": [
            { "name": "productCode", "type": "text" },
            { "name": "quantity", "type": "number" }
          ]
        }
      ],
      "links": [
        { "rel": [ "self" ], "href": "http://api.x.io/orders/42" },
        { "rel": [ "previous" ], "href": "http://api.x.io/orders/41" },
        { "rel": [ "next" ], "href": "http://api.x.io/orders/43" }
      ]
    }
    siren_builder = SirenBuilder()
    siren_obj = siren_builder.from_api_response(response)

We could then access the various properties on the
object.

.. code-block:: python

    >>> print(siren_obj.orderNumber)
    42
    >>> print(siren_obj.itemCount)
    3
    >>> print(siren_obj.status)
    pending

Additionally, we could see that the class name was indeed order

.. code-block:: python

    >>> print(siren_obj.__class__.__name__)
    order

Where you can really see the power of the SIREN protocol is
when you go to perform actions.  In this case, we can see that
there is an action called add-item.  We can simply call that
on the siren_obj and we will get a new SIREN object representing
the response from the server for adding an item.

.. code-block:: python

    >>> new_item = siren_obj.add_item(productCode=15, quantity=2)

And now we have the new item that was added to the orders items!

Additionally, we can access links and entities

.. code-block:: python

    >>> next_obj = siren_obj.get_links('next')[0].as_python_object()
    >>> customer = next(siren_obj.get_entity('customer'))
    
