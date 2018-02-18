.. httpbase documentation master file, created by
   sphinx-quickstart on Sat Feb 17 20:05:07 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. _index:

httpbase Client Library
***********************

``httpbase`` is base library for creating HTTP clients with as little boilerplate as possible. It is built on top of the
excellent ``requests`` library and inspired in design by the Django REST Framework. It can be used in scripts for
automating tasks as well as the base for client libraries for inter-service communication.


Getting Started
===============

Some resources that can help you get up to started.

.. toctree::
   :hidden:

   getting_started/index

* :doc:`getting_started/installation`

* :doc:`getting_started/example` provides an example client to interact with the `JSONPlaceholder`_ API

.. _JSONPlaceholder: https://jsonplaceholder.typicode.com/


API Documentation
=================

Comprehensive reference material for the API exposed by ``httpbase`` can be found in the :doc:`api/index`

.. toctree::
   :hidden:
   :maxdepth: 1
   :glob:

   api/index
