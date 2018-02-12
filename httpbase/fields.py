from typing import Callable

from .constants import _marker
from .exceptions import ImmutableFieldError, NonNullableField


def _default_validator(value):
    return value


class Field(object):
    def __init__(self, label: str=None, nullable: bool=False, default=None,
                 immutable: bool=False, validator: Callable=_default_validator, **kwargs):
        self.label = label
        self.value = None
        self.nullable = nullable
        self.default = default
        self.immutable = immutable
        self.validator = validator

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value}>"

    def to_value(self):
        return self.validator(self.value)

    def set_value(self, value):
        if self.immutable:
            raise ImmutableFieldError(f"{self} has been set as immutable")
        if value is None and not self.nullable:
            raise NonNullableField(f"{self} cannot be null")
        if value is _marker:
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
            kwargs["validator"] = int
        super().__init__(**kwargs)


class ResourceField(Field):
    def to_value(self):
        values = {}
        for _, field in self.value.fields.items():
            values[field.label] = field.to_value()
        return values


class ListField(Field):
    def to_value(self):
        return [self.validator(val) for val in self.value]


class MapField(Field):
    def to_value(self):
        return {key: self.validator(value) for key, value in self.value}
