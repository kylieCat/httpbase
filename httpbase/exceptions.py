class RouteError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class SerializationError(Exception):
    pass


class ImmutableFieldError(Exception):
    pass


class NonNullableField(Exception):
    pass
