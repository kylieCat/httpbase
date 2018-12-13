import json
from unittest import TestCase, mock

from httpbase.client import HTTPBaseClient
from httpbase.constants import HTTPMethods, HTTPResponseCodes
from httpbase.routes import Route


class TestHTTPClient(HTTPBaseClient):
    pass


class TestClient(TestCase):
    def setUp(self):
        self.client = TestHTTPClient(baseurl="http://example.com")
        self.route = Route("/api/foo", HTTPMethods.GET, params={"baz", "qux"})
        self.kwargs = {
            "data": json.dumps({"foo": "bar"}),
            "foo": 123,
            "bar": "abc",
            "headers": {"Content-Type": "application/json"}
        }

    def test_is_route_kwarg(self):
        test_data = {
            "foo": False,
            "baz": False,
            "qux": False,
            "abc": False,
            "def": False,
            "123": False,
            "data": True,
            "json": True,
            "params": True,
        }
        for key, expected in test_data.items():
            self.assertEqual(self.client._is_requests_kwarg(key), expected)

    def test_strip_route_kwargs(self):
        stripped = self.client._strip_route_kwargs(self.kwargs)
        for v in self.route.vars:
            self.assertNotIn(v, stripped)
        for p in self.route.params:
            self.assertNotIn(p, stripped)

    def test_prep_request(self):
        actual = self.client._prep_request(**self.kwargs)
        expected = {"data": json.dumps({"foo": "bar"}), "headers": {"Content-Type": "application/json"}}
        self.assertEqual(actual, expected)

    @mock.patch("httpbase.client.requests.request")
    def test_make_request(self, mock_requests):
        self.client._make_request(self.route, **self.kwargs)
        mock_requests.assert_called_with(
            "get",
            "http://example.com/api/foo",
            data=json.dumps({"foo": "bar"}),
            headers={"Content-Type": "application/json"}
        )

    @mock.patch("httpbase.client.requests.request")
    def test_error_response(self, mock_requests):
        kwargs = {
            "data": json.dumps({"foo": "bar"}),
            "headers": {"Content-Type": "application/json"}
        }
        route = Route("/api/foo/{foo_id}", HTTPMethods.GET)
        resp = self.client._make_request(route, **kwargs)
        self.assertEqual(resp.status_code, HTTPResponseCodes.BAD_REQUEST)
        self.assertIn("message", resp.json())
        mock_requests.assert_not_called()
