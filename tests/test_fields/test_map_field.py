from unittest import TestCase
import string

from httpbase.fields import MapField
from httpbase.exceptions import SerializationError, NonNullableField
from httpbase.resources import Resource


class TestMapField(TestCase):
    def test_dict_field(self):
        value = {"a": 1, "b": 2, "c": "a"}

        class Foo(Resource):
            foo = MapField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)

    def test_nullable(self):
        class Foo(Resource):
            foo = MapField(label="foo", nullable=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {"foo": None})
        self.assertFalse(resource.errors)

        class Foo(Resource):
            foo = MapField(label="foo")

        with self.assertRaises(NonNullableField):
            Foo(foo=None)

    def test_default(self):
        value = {"a": 1, "b": 2, "c": "a"}

        class Foo(Resource):
            foo = MapField(label="foo", default=value)

        resource = Foo()
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)

    def test_validator(self):
        value = {"a": 1, "b": 2, "c": "a"}

        def value_is_letter(value):
            if value is not None:
                return value
            else:
                raise TypeError("not in alphabet")

        class Foo(Resource):
            foo = MapField(label="foo", validator=value_is_letter)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)

        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)

        resource = Foo(foo={"a": 1, "b": 2, "c": None})
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_printable(self):
        value = {"a": 1, "b": 2, "c": "a"}

        class Foo(Resource):
            foo = MapField(label="foo", printable=False)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)
        self.assertNotIn(str(value), repr(resource.foo))

    def test_omit_null(self):
        class Foo(Resource):
            foo = MapField(label="foo", nullable=True, omit_null=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {})
        self.assertFalse(resource.errors)
