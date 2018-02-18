.. _constants_module:

:mod:`httpbase.constants`
--------------------------------

Constants
~~~~~~~~~

Constants used within the library and suitable for use in packages that build on top of it.

.. automodule:: httpbase.constants

  .. c:var:: DEFAULT_DATE_FORMAT

    The default date format for :class:`~httpbase.fields.DateField`. Value: ``"%Y-%m-%d %H:%M:%s"``

  .. c:var:: TEMPLATE_VARIABLE_PATTERN

    The regex pattern used to find template variables in :class:`~httpbase.routes.Route`. Value: ``r"{(\w+)}"``

  .. class:: HTTPMethods

    Container class for HTTP request methods.

  .. class:: HTTPResponseCodes

    Container class for HTTP response codes.

  .. autoclass:: null
