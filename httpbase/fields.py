from typing import Callable

from .constants import null, DEFAULT_DATE_FORMAT
from .exceptions import NonNullableField


def _default_validator(value):
    if isinstance(value, (int, str, float, bool, bytes)) or value is None:
        return value
    else:
        raise TypeError(
            "value is not a JSON serializable value or is a container. Add a custom validator or use a container field"
        )


class Field(object):
    """Base class for the fields on a ``Resource``.

     ``Field`` are containers for values that know how to serialize the values they contain.
    """
    def __init__(self, label: str=None, nullable: bool=False, default=null,
                 validator: Callable=_default_validator, **kwargs):
        self.label = label
        self.value = None
        self.nullable = nullable
        self.default = default
        self.validator = validator
        self.printable: bool = kwargs.get("printable", True)
        self.omit_null: bool = kwargs.get("omit_null", False)

    def _set_parent(self, parent):
        if parent is None:
            from .resources import Resource
            parent = Resource
        self.parent = parent

    def __repr__(self):
        if self.printable:
            message = f"<{self.__class__.__name__}: {self.value}>"
        else:
            message = f"<{self.__class__.__name__}: XXXXXX>"
        return message

    def to_value(self, **kwargs):
        # Don't attempt to validate null values
        if self.nullable and self.value is None:
            return self.value
        return self.validator(self.value)

    def set_value(self, value):
        if value is None:
            if not self.nullable and self.default is null:
                raise NonNullableField(f"{self.parent.__class__.__name__}.{self.label} cannot be null")
            else:
                value = self.default
        self.value = value


class IntField(Field):
    def __init__(self, **kwargs):
        if "validator" not in kwargs:
            kwargs["validator"] = int
        super().__init__(**kwargs)


class StrField(Field):
    def __init__(self, **kwargs):
        if "validator" not in kwargs:
            kwargs["validator"] = str
        super().__init__(**kwargs)


class BoolField(Field):
    def __init__(self, **kwargs):
        if kwargs.get("nullable"):
            raise NonNullableField(f"{self.__class__.__name__} cannot be null")
        super().__init__(**kwargs)

    def to_value(self, **kwargs):
        return bool(self.value)


class ResourceField(Field):
    def to_value(self, **kwargs):
        use_labels = kwargs.get("use_labels", True)
        if self.value is None and self.nullable:
            return self.default
        values = {}
        for key, field in self.value.fields.items():
            label = self._get_json_key(key, field, use_labels)
            values[label] = field.to_value()
        return values

    def _get_json_key(self, key, field, use_label):
        if use_label:
            label = field.label
        else:
            label = key
        return label


class ListField(Field):
    """
    Field for value thatshould be serialized as strings.
    """
    def to_value(self, **kwargs):
        if self.value is None and self.nullable:
            return self.default
        return [self.validator(val) for val in self.value]


class MapField(Field):
    def to_value(self, **kwargs):
        if self.value is None and self.nullable:
            return self.default
        return {key: self.validator(value) for key, value in self.value.items()}


class DateField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.format = kwargs.get("format", DEFAULT_DATE_FORMAT)

    def to_value(self, **kwargs):
        try:
            return self.value.strftime(self.format)
        except AttributeError:
            raise TypeError(f"value {self.value} of type {self.value.__class__.__name__} can't be serialized as a date.")


class EpochField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_seconds = kwargs.get("total_seconds", True)

    def to_value(self, **kwargs):
        try:
            if self.total_seconds:
                return self.value.timestamp()
            return int(self.value.timestamp())
        except AttributeError:
            raise TypeError(f"Failed to serialize {self}. Expected 'datetime' got {self.value.__class__.__name__}")
