import json
from typing import Dict, Union, Mapping, List

# Types for checking
JSON = Union[str, int, float, bool, None, Mapping[str, 'JSON'], List['JSON']]


class Resource(object):
    """
    Base class for classes that should JSON serializable.

    Class attrs:
        mapped_fields: Some fields have a different name on class instances than they do within the JSON spec of
        the service you are communicating with. This can happen for a few reasons (snake case vs camel case) so add
        mappings here if that comes up. This is a very naive solution but it should work for most cases.
        Dict[class_attr, api_field]
    """
    _mapped_fields: Dict[str, str] = {}

    def dict(self) -> Dict[str, JSON]:
        """
        Returns a dictionary suitable for use with `json.dumps()`. If your subclass has complex types as
        values you should override this and make it so that the call to `your_class.dict()` will return something JSON
        serializable.
        """
        return {self._mapped_fields.get(k, k): v for k, v in self.__dict__.items() if not k.startswith("_")}

    def json(self) -> JSON:
        """
        Get the JSON for an instance
        """
        return json.dumps(self.dict())
