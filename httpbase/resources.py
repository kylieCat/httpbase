import copy
import json
from typing import Dict, Union, Mapping, List

from .exceptions import SerializationError
from .fields import Field

# Types for checking
JSON = Union[str, int, float, bool, None, Mapping[str, 'JSON'], List['JSON']]


class ResourceMetaclass(type):
    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        fields = [
            (field_name, attrs.pop(field_name)) for field_name, obj in list(attrs.items()) if isinstance(obj, Field)
        ]

        for base in reversed(bases):
            if hasattr(base, '_declared_fields'):
                fields = [
                    (field_name, obj) for field_name, obj
                    in base._declared_fields.items()
                    if field_name not in attrs
                ] + fields

        return dict(fields)

    def __new__(cls, name, bases, attrs):
        attrs['_declared_fields'] = cls._get_declared_fields(bases, attrs)
        return super(ResourceMetaclass, cls).__new__(cls, name, bases, attrs)


class Resource(metaclass=ResourceMetaclass):
    SerializationError = SerializationError

    def __init__(self, **kwargs):
        self._errors = {}
        self._fields = {}
        kwargs["_parent"] = self
        for key, field in self.fields.items():
            field = self.fields.get(key)
            field.set_value(kwargs.get(key))
            setattr(self, key, field)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    def fields(self) -> Dict[str, Field]:
        if not self._fields:
            self._fields = {key: value for key, value in copy.deepcopy(self._declared_fields).items()}
        return self._fields

    @property
    def errors(self) -> Dict:
        return {key: value for key, value in self._errors.items()}

    def dict(self) -> Dict[str, JSON]:
        """
        Returns a dictionary suitable for use with `json.dumps()`. If your subclass has complex types as
        values you should override this and make it so that the call to `your_class.dict()` will return something JSON
        serializable.
        """
        result = {}
        for key, field in self.fields.items():
            try:
                result[field.label] = field.to_value()
            except (TypeError, AttributeError):
                self._errors[key] = field.value.__class__.__name__
        return result

    def json(self) -> str:
        """
        Get the JSON for an instance.

        Raises:
            SerializationError: Raises a ``SerializationError`` if there are fields that aren't JSON serializable.
        """
        d = self.dict()
        if self.errors:
            msg = "fields with types {} could not be serialized".format([(k, v) for k, v in self.errors.items()])
            raise SerializationError(msg)
        return json.dumps(d)
