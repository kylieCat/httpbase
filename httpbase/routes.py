from typing import NamedTuple, Set
from urllib import parse

from .exceptions import RouteError


class Route(NamedTuple):
    """
    A route definition. Contains a relative path, the HTTP method to use, a set containing the names of template
    variables (``user_id`` in ``/api/users/{user_id}``) and a set of usable query parameters.

    """
    path: str
    method: str
    vars: Set[str] = set()
    params: Set[str] = set()

    def get_url(self, baseurl: str, **params):
        if not all((var in params for var in self.vars)):
            raise RouteError("missing required template variables for route: {}".format(self.vars))
        return parse.urljoin(baseurl, self.path.format(**params))
