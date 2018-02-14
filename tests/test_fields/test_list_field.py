from unittest import TestCase
import string

from httpbase.fields import ListField
from httpbase.exceptions import SerializationError, NonNullableField
from httpbase.resources import Resource


class TestListField(TestCase):
    def test_list_field(self):
        value = ["a", "b", "c"]

        class Foo(Resource):
            foo = ListField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)

    def test_nullable(self):
        class Foo(Resource):
            foo = ListField(label="foo", nullable=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {"foo": None})
        self.assertFalse(resource.errors)

        class Foo(Resource):
            foo = ListField(label="foo")

        with self.assertRaises(NonNullableField):
            Foo(foo=None)

    def test_default(self):
        value = ["a", "b", "c"]

        class Foo(Resource):
            foo = ListField(label="foo", default=value)

        resource = Foo()
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)

    def test_validator(self):
        value = ["a", "b", "c"]

        def value_is_letter(value):
            if value in string.ascii_letters:
                return value
            else:
                raise TypeError("not in alphabet")

        class Foo(Resource):
            foo = ListField(label="foo", validator=value_is_letter)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)

        resource = Foo(foo=[1, 2, 3])
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_printable(self):
        value = ["a", "b", "c"]

        class Foo(Resource):
            foo = ListField(label="foo", printable=False)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertFalse(resource.errors)
        self.assertNotIn(str(value), repr(resource.foo))

    def test_omit_null(self):
        class Foo(Resource):
            foo = ListField(label="foo", nullable=True, omit_null=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {})
        self.assertFalse(resource.errors)
