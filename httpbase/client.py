import json

import requests

from .constants import HTTPResponseCodes, _RequestsKwargs
from .exceptions import ConfigurationError, RouteError
from .routes import Route


_request_kwargs = _RequestsKwargs()


def _get_error_response(code: int, message: str) -> requests.Response:
    """"""
    resp = requests.Response()
    resp.status_code = code
    resp.headers = {"Content-Type": "application/json"}
    resp._content = json.dumps({"message": "error making request: {}".format(message)}).encode()
    return resp


class HTTPBaseClient(object):
    """Base class for HTTP clients.

    Subclass this to provide a solid base for HTTP client classes. Handles getting URL's from ```Route`` objects,
    parsing kwargs, injecting headers, and does the work of actually sending the request. Some of these can be
    overridden to extend functionality as required. However in the most basic of cases you'll only have to subclass this
    class, and call ``_make_request(Route, **kwargs)``.

    The most basic use case of making a ``GET`` request to an unauthenticated API might look like::

        class TemperatureAPIClient(HTTPBaseClient):
            _baseurl = "http://temperature.com

            def get_temperature(self, zip_code):
                return self._make_request(
                    Route("/temperatures/{zip_code}", HTTPMethods.GET),
                    zip_code=zip_code
                )


    In a simple example like the one above you may not even need to create any ``Resource`` classes. A more complete
    might be::

        class TemperatureDataResource(Resource):
            temperature = FloatField(label="temp")
            zip_code = StrField(validator=max_length_is_six)


        class TemperatureAPIClient(HTTPBaseClient):
            baseurl = "http://temperature.com

            def get_temperature(self, zip_code):
                return self._make_request(
                    Route("/temperatures/{zip_code}", HTTPMethods.GET),
                    zip_code=zip_code
                )

            def post_temperature_data(self, temp_data):
                return self._make_request(
                    Route("/temperature", HTTPMethods.POST),
                    data=temp_data.json()
                )

    Methods:
         __init__(*list, **dict) -> HTTPBaseClient
         _inject_headers(dict[str, str]) -> dict
         _is_requests_kwarg(str) -> bool
         _strip_route_kwargs(dict) -> dict
         _prep_request(**dict) -> dict
         _make_request(Route, **dict) -> requests.Response
    """
    baseurl = None

    def __init__(self, *args, **kwargs):
        self.baseurl = kwargs.get("baseurl", self.baseurl)

        if self.baseurl is None:
            raise ConfigurationError(
                "'baseurl' must be provided as a class attribute or as a keyword argument to __init__"
            )

    ConfigurationError = ConfigurationError

    def _inject_headers(self, req_kwargs: dict) -> dict:
        """
        Inject any additional headers users may not have added or shouldn't need to know about. This method can and
        probably should be overridden. When overriding don't forget to check for and update any existing headers. Don't
        just blindly overwrite them.

        Args:
            req_kwargs: A dictionary of kwargs with the route specific values removed. May contain a ``headers`` key
                already.
        """
        return req_kwargs

    @staticmethod
    def _is_requests_kwarg(key: str) -> bool:
        """
        Checks whether or not a given key belongs is one fo the kwargs ``requests`` accepts. This probably shouldn't be
        overridden.

        Args:
            key: A dictionary key. Will be checked against ``constants._RequestsKwargs``
        """
        return key in _request_kwargs

    def _strip_route_kwargs(self, kwargs: dict) -> dict:
        """
        Removes kwargs that come from client methods. ``requests`` will choke on unexpected kwargs so this needs
        to be done. If this method is overridden it should still return a dictionary that can be consumed by
        ``requests``.

        Args:
            kwargs: The kwargs form the client methods
        """
        return {key: value for key, value in kwargs.items() if self._is_requests_kwarg(key)}

    def _prep_request(self, **kwargs) -> dict:
        """
        Remove kwargs that ``requests`` will choke on and add any missing required headers.

        Args:
            route: The ``Route`` corresponding to the request.
            **kwargs:
        """
        req_kwargs = self._strip_route_kwargs(kwargs)
        req_kwargs = self._inject_headers(req_kwargs)
        return req_kwargs

    def _make_request(self, route: Route, **kwargs) -> requests.Response:
        """
        This method does a few things
            - Separates kwargs meant for the underlying ``requests`` framework from kwargs
              we care about (query params and URL templating variables).
            - Injects required headers (auth and content type).
            - Formats the full URL. Formats in things like resource ID's and attaches query params.
            - Finally sends request and returns the response.

        Args:
            route: The route for the request. Contains the path, HTTP method, template variable names for the URL and
                accepted query params.

        Keyword Args:
            params:  Dictionary or bytes to be sent in the query string for the request.
            data:  Dictionary, bytes, or file-like object to send in the body of the request.
            json:  json to send in the body of the request.
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
            kwargs: any additional kwargs your client specific client methods might need.
        """
        req_kwargs = self._prep_request(**kwargs)
        try:
            url = route.get_url(self.baseurl, **kwargs)
            return requests.request(route.method, url, **req_kwargs)
        except RouteError as err:
            return _get_error_response(HTTPResponseCodes.BAD_REQUEST, str(err))
