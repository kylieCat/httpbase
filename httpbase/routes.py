import re
from typing import NamedTuple, Set
from urllib import parse

from .exceptions import RouteError


REGEX = re.compile(r"{(\w+)}")


class Route(object):
    """
    A route definition. Contains a relative path, the HTTP method to use, a set containing the names of template
    variables (``user_id`` in ``/api/users/{user_id}``) and a set of usable query parameters.

    """
    def __init__(self, path: str, method: str, params: set=None):
        self.path = path
        self.method = method
        self.vars = REGEX.findall(self.path)
        if params is None:
            params = set()
        self.params = params

    def get_url(self, baseurl: str, **params):
        if not all((var in params for var in self.vars)):
            raise RouteError("missing required template variables for route: {}".format(self.vars))
        return parse.urljoin(baseurl, self.path.format(**params))
