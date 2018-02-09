from unittest import TestCase

from httpbase.constants import HTTPMethods
from httpbase.exceptions import RouteError
from httpbase.routes import Route


class TesRoutes(TestCase):
    def setUp(self):
        self.baseurl = "http://example.com"
        self.foo_id = 123

    def test_get_url(self):
        route = Route("/api/foo/{foo_id}", HTTPMethods.GET)
        expected = "http://example.com/api/foo/123"
        actual = route.get_url(self.baseurl, foo_id=self.foo_id)
        self.assertEqual(expected, actual)

        route = Route("/api/foo/{foo_id}/{baz}", HTTPMethods.GET)
        expected = "http://example.com/api/foo/123/qux"
        actual = route.get_url(self.baseurl, foo_id=self.foo_id, baz="qux")
        self.assertEqual(expected, actual)

        with self.assertRaises(RouteError):
            route = Route("/api/foo/{foo_id}/{baz}", HTTPMethods.GET)
            route.get_url(self.baseurl, foo_id=self.foo_id)
