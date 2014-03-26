django-sixpack
==============


``django-sixpack`` is a Django-friendly wrapper for the `sixpack-py <https://github.com/seatgeek/sixpack-py>`_ 
client library to `SeatGeek <https://github.com/seatgeek/>`_'s `Sixpack <https://github.com/seatgeek/sixpack>`_,
a language-agnostic A/B testing framework.

This is not a full-fledged client (it relies on ``sixpack-py`` for the actual connection); it's a wrapper
to make using ``sixpack-py`` more friendly and declarative.


Install
-------

.. code:: bash

   pip install django-sixpack

Configuration
-------------

Set ``SIXPACK_HOST`` and (optionally) ``SIXPACK_TIMEOUT`` in your settings file. 

If ``SIXPACK_HOST`` is unset, it will fall back to ``sixpack-py``'s default, which is ``http://localhost:5000``. If ``SIXPACK_HOST`` is set to ``None``, ``django-sixpack`` will
operate in test mode, which means that the control alternative (the first one listed) will be
returned for all ``participate`` calls, all ``convert`` calls will be successful, and the exertnal
sixpack server will not be contacted.

Usage
-----

First, define a test somewhere:

.. code:: python
   
   from djsixpack.djsixpack import SixpackTest
   
   class ButtonColorTest(SixpackTest):
      alternatives = (
         'RED',
         'BLUE'
      )
      
If you go into the Sixpack web dashboard, you'll see this as a test called ``button_color``, with 
the control being the alternative ``RED`` (the first alternative listed will be considered the control).

When it's time to add a user to the test:

.. code:: python
   
   expt = ButtonColorTest(request.user)
   bucket = expt.participate()
   
   context = {}
   if bucket == ButtonColorTest.RED:
      context = {'color': '#FF0000'}
   elif bucket == ButtonColorTest.BLUE:
      context = {'color': '#0000FF'}
      
``SixpackTest.participate`` will return the alternative ``request.user`` is bucketed into - and all alternatives
will be available as class properties. 

When instantiating a ``SixpackTest`` test, the only argument the constructor takes is the model instance
which is used to represent the person seeing this test. By default, ``SixpackTest`` will use the instance's
``pk`` attribute as the unique identifier to represent this person - but this can be overridden by setting the
``unique_attr`` class attribute.

For example, you could have a ``Business`` model class which represents a person, and it has a attribute called 
``global_id`` which represents a cross-platform way of identifying a particular ``Business``. In that case, 
you could do:

.. code:: python
   
   from djsixpack.djsixpack import SixpackTest
   
   class ButtonColorTest(SixpackTest):
      unique_attr = 'global_id'
      alternatives = (
         'RED',
         'BLUE'
      )

At any point, you can check the ``SixpackTest.client_id`` property to see what's being used as the ``client_id``.

If something ever goes wrong - a request times out, the ``sixpack`` server disappears, etc. - all ``participate`` 
calls will return the control alternative, and all ``convert`` calls will seem successful (and we'll note this happend
in the log).

License
-------

``django-sixpack`` is released under the MIT license.


Contribute
----------

- Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug
- Fork the repository on GitHub to start making your changes to the master branch (or branch off of it)
- Send a pull request and bug the maintainer until it gets merged and published
- Add yourself to the ``AUTHORS`` file


Thanks
------

- `SeatGeek <https://github.com/seatgeek/>`_, for being great
