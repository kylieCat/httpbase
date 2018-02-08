import json

import requests

from .constants import HTTPResponseCodes
from .exceptions import ConfigurationError, RouteError
from .routes import Route


def _get_error_response(code: int, message: str) -> requests.Response:
    resp = requests.Response()
    resp.status_code = code
    resp.headers = {"Content-Type": "application/json"}
    resp._content = json.dumps({"message": "error making request: {}".format(message)}).encode()
    return resp


class HTTPBaseClient(object):
    def __init__(self, baseurl, *args, **kwargs):
        self.baseurl = baseurl

    ConfigurationError = ConfigurationError

    def _inject_headers(self, req_kwargs: dict) -> dict:
        """
        Inject any additional headers users may not have added or shouldn't need to know about.

        Args:
            req_kwargs: A dictionary of kwargs with the route specific values removed.
        """
        return req_kwargs

    @staticmethod
    def _is_route_kwarg(key: str, route: Route) -> bool:
        """
        Checks whether or not a given key belongs to a route.

        Args:
            key: A dictionary key
            route: A route object.
        """
        return key in route.vars or key in route.params

    def _strip_route_kwargs(self, kwargs: dict, route: Route) -> dict:
        """
        Removes kwargs that come from client methods. ``requests`` will choke on unexpected kwargs so this needs
        to be done.

        Args:
            kwargs: The kwargs form the client methods
            route: A route object
        """
        return {key: value for key, value in kwargs.items() if not self._is_route_kwarg(key, route)}

    def _prep_request(self, route: Route, **kwargs) -> dict:
        """
        Remove kwargs that ``requests`` will choke on and add any missing required headers.

        Args:
            route: The ``Route`` corresponding to the request.
            **kwargs:
        """
        req_kwargs = self._strip_route_kwargs(kwargs, route)
        req_kwargs = self._inject_headers(req_kwargs)
        return req_kwargs

    def _make_request(self, route: Route, **kwargs) -> requests.Response:
        """
        This method does a few things:
            - Separates kwargs meant for the underlying ``requests`` framework from kwargs
              we care about (query params and URL templating variables).
            - Injects required headers (auth and content type).
            - Formats the full URL. Formats in things like resource ID's and attaches query params.
            - Finally sends request and returns the response.

        Args:
            route: The route for the request. Contains the path, HTTP method, template variable names for the URL and
                accepted query params.
            **kwargs: Takes several optional kwargs to build the request:
                params:  Dictionary or bytes to be sent in the query string for the :class:`Request`.
                data:  Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
                json:  json to send in the body of the
                    :class:`Request`.
                headers:  Dictionary of HTTP Headers to send with the
                cookies:  Dict or CookieJar object to send with the
                files:  Dictionary of ``'filename': file-like-objects`` for multipart encoding upload.
                auth:  Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
                timeout:  How long to wait for the server to send data before giving up, as a float, or a
                    `(connect timeout, read timeout) <timeouts>` tuple.
                allow_redirects:  Set to True by default.
                proxies:  Dictionary mapping protocol or protocol and hostname to the URL of the proxy.
                stream:  whether to immediately download the response content. Defaults to ``False``.
                verify:  Either a boolean, in which case it controls whether we verify the server's TLS certificate,
                    or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
                cert:  if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.

                As well as any additional kwargs your client specific client methods might need.
        """
        req_kwargs = self._prep_request(route, **kwargs)
        try:
            url = route.get_url(self.baseurl, **kwargs)
            return requests.request(route.method, url, **req_kwargs)
        except RouteError as err:
            return _get_error_response(HTTPResponseCodes.BAD_REQUEST, str(err))
