from unittest import TestCase

from httpbase import fields
from httpbase.exceptions import SerializationError
from httpbase.resources import Resource


class TestIntField(TestCase):
    def test_int_field(self):
        value = 15

        class Foo(Resource):
            foo = fields.IntField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

    def test_nullable(self):
        class Foo(Resource):
            foo = fields.IntField(label="foo", nullable=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {"foo": None})

    def test_default(self):
        value = 15

        class Foo(Resource):
            foo = fields.IntField(label="foo", default=value)

        resource = Foo()
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

    def test_default_validator(self):
        value = "abc"

        class Foo(Resource):
            foo = fields.IntField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_validator(self):
        value = 15

        def value_in_range(value):
            if 10 < value < 20:
                return value
            else:
                raise TypeError("not in range")

        class Foo(Resource):
            foo = fields.IntField(label="foo", validator=value_in_range)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

        resource = Foo(foo=35)
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_printable(self):
        value = 15

        class Foo(Resource):
            foo = fields.IntField(label="foo", printable=False)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertNotIn(str(value), repr(resource.foo))

    def test_omit_null(self):
        class Foo(Resource):
            foo = fields.IntField(label="foo", nullable=True, omit_null=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {})
