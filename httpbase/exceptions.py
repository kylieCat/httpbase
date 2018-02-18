class RouteError(Exception):
    """
    Used to indicate that there was an error that originated form a ``Route`` object. An example being when a ``Route``
    is passed to a client method and the template variables for the ``path`` attribute aren't passe din as well.
    """
    pass


class ConfigurationError(Exception):
    """
    This error is used to indicate an error with client configuration. A missing base URL, missing API keys, or
    incorrectly set or missing headers provided by consuming code.
    """
    pass


class SerializationError(Exception):
    """This error is used to indicate that an exception occurred during serialization of the fields on a resource."""
    pass


class ImmutableFieldError(Exception):
    pass


class NonNullableField(Exception):
    """
    Raised when a field that has ``nullable==False`` is initialized without a value provided in the the resource
    constructor and no default is set.
    """
    pass
