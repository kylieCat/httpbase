import copy
import json
from typing import Dict, Union, Mapping, List

from .constants import null
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
        self.parent = None
        for key, field in self.fields.items():
            field._set_parent(self)
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

    def dict(self, use_labels=True) -> Dict[str, JSON]:
        """
        Returns a dictionary suitable for use with `json.dumps()`. If your subclass has complex types as
        values you should override this and make it so that the call to `your_class.dict()` will return something JSON
        serializable.
        """
        result = {}
        for key, field in self.fields.items():
            try:
                if use_labels:
                    label = field.label
                else:
                    label = key
                if field.omit_null and field.value is null:
                    continue
                elif field.value is null:
                    result[label] = None
                else:
                    result[label] = field.to_value(use_labels=use_labels)
            except (TypeError, AttributeError, ValueError) as err:
                self._errors[key] = f"error from validator: {str(err)}"
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

    def _traverse_fields(self, path, default=None):
        field = self
        levels, target = path.split(".")[:-1], path.split(".")[-1]
        for level in levels:
            field = getattr(field, level).value
        if default is None:
            default = field
        return getattr(field, target, default)

    def get(self, path):
        target = self._traverse_fields(path)
        return target

    def get_value(self, path):
        target = self._traverse_fields(path)
        return target.value

    def update(self, path, value):
        target = self._traverse_fields(path)
        target.set_value(value)

    def get_label(self, path):
        target = self._traverse_fields(path)
        return target.label

    def labels(self, path=""):
        target = self._traverse_fields(path)
        if not hasattr(target, "fields"):
            target = target.value
        for key, field in target.fields.items():
            yield field.label
