import json
from typing import Dict, Union, Mapping, List, Any, Tuple

from .exceptions import SerializationError

# Types for checking
JSON = Union[str, int, float, bool, None, Mapping[str, 'JSON'], List['JSON']]


class Resource(object):
    """
    Base class for classes that should JSON serializable.

    Class attrs:
        mapped_fields: Some fields have a different name on class instances than they do within the JSON spec of
        the service you are communicating with. This can happen for a few reasons (snake case vs camel case) so add
        mappings here if that comes up. This is a very naive solution but it should work for most cases.
        List[Tuple[class_attr, api_field]]

    Returns:
        dict[str, JSON], dict[str, str]: Returns a dictionary that is safe to JSON serialize. It also returns a
            dictionary of the names and types of fields that aren't JSON serializable by default. What you do with this
            information is up to you.
    """
    mapped_fields: List[Tuple[str, str]] = []
    _api_to_client = {}
    _client_to_api = {}
    SerializationError = SerializationError

    def __init__(self, *args, **kwargs):
        self._api_to_client = {k: v for k, v in self.mapped_fields}
        self._client_to_api = {v: k for v, k in self.mapped_fields}

    def _serialize_sequence(self, seq: Union[List, Tuple]) -> Tuple[List, Any]:
        """
        Serializes sequences into a list of ``json.dumps`` safe values. If everything in the sequence is JSON
        serializable a list of values will be returned. Does recurse over other container types found in the sequence.

        Args:
            seq: A Python sequence, ``list`` or ``tuple``

        Returns:
            result, error: If everything is serializable returns a list of values and ``None``. If something couldn't
                be serialized returns ``None`` and a value to be used in collecting errors.
        """
        result, error = [], None
        for ele in seq:
            r, error = self._serialize_field_value(ele)
            if error:
                result, error = None, error
                break
            else:
                result.append(r)
        return result, error

    def _serialize_dict(self, d: Dict) -> Tuple[Dict, Any]:
        """
        Serializes dictionaries into a dict of ``json.dumps`` safe values. If everything in the sequence is JSON
        serializable a dictionary and no error will be returned. Does recurse over other container types found in the
        dictionary.

        Args:
            d:

        Returns:
            result, error: If everything is serializable returns a dict of values and ``None``. If something couldn't
                be serialized returns ``None`` and a value to be used in collecting errors.
        """
        result, error = {}, None
        for k, v in d.items():
            r, error = self._serialize_field_value(v)
            if error:
                result = None, error
                break
            else:
                result[k] = r
        return result, error

    def _serialize_field_value(self, value: Any) -> Tuple[JSON, str]:
        result, error = None, None
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value, error
        elif isinstance(value, Resource):
            result, error = value.dict()
        elif isinstance(value, (list, tuple)):
            result, error = self._serialize_sequence(value)
        elif isinstance(value, dict):
            result, error = self._serialize_dict(value)
        else:
            error = value.__class__.__name__
        return result, error

    def dict(self) -> Tuple[Dict[str, JSON], Dict[str, str]]:
        """
        Returns a dictionary suitable for use with `json.dumps()`. If your subclass has complex types as
        values you should override this and make it so that the call to `your_class.dict()` will return something JSON
        serializable.
        """
        results, errors = {}, {}
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                field = self._client_to_api.get(k, k)
                result, error = self._serialize_field_value(v)
                if error:
                    errors[field] = error
                else:
                    results[field] = result
        return results, errors

    def json(self) -> JSON:
        """
        Get the JSON for an instance.

        Raises:
            SerializationError: Raises a ``SerializationError`` if there are fields that aren't JSON serializable.
        """
        d, errors = self.dict()
        if errors:
            msg = "fields of types {} are not JSON serializable".format([(k, v) for k, v in errors.items()])
            raise SerializationError(msg)
        return json.dumps(d)
