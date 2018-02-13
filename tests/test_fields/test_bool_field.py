from unittest import TestCase

from httpbase.fields import BoolField
from httpbase.exceptions import SerializationError, NonNullableField
from httpbase.resources import Resource


class TestBoolField(TestCase):
    def test_bool_field(self):
        value = True

        class Foo(Resource):
            foo = BoolField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

    def test_nullable(self):
        with self.assertRaises(NonNullableField):
            class Foo(Resource):
                foo = BoolField(label="foo", nullable=True)

    def test_default(self):
        value = True

        class Foo(Resource):
            foo = BoolField(label="foo", default=value)

        resource = Foo()
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})

    def test_printable(self):
        value = True

        class Foo(Resource):
            foo = BoolField(label="foo", printable=False)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": value})
        self.assertNotIn(str(value), repr(resource.foo))
