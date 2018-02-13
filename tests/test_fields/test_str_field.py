from unittest import TestCase

from httpbase.fields import StrField
from httpbase.exceptions import SerializationError
from httpbase.resources import Resource


class TestStrField(TestCase):
    def test_str_field(self):
        value = "abc"

        class Foo(Resource):
            foo = StrField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

    def test_nullable(self):
        class Foo(Resource):
            foo = StrField(label="foo", nullable=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {"foo": None})

    def test_default(self):
        value = "abc"

        class Foo(Resource):
            foo = StrField(label="foo", default=value)

        resource = Foo()
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

    def test_validator(self):
        value = "abc"

        def value_in_range(value):
            if len(value) < 10:
                return value
            else:
                raise TypeError("not in range")

        class Foo(Resource):
            foo = StrField(label="foo", validator=value_in_range)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

        resource = Foo(foo="1234567891011")
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_printable(self):
        value = "abc"

        class Foo(Resource):
            foo = StrField(label="foo", printable=False)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertNotIn(str(value), repr(resource.foo))

    def test_omit_null(self):
        class Foo(Resource):
            foo = StrField(label="foo", nullable=True, omit_null=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {})
