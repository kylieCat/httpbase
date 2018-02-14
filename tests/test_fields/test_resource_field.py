import operator
from unittest import TestCase, mock

from httpbase.fields import ResourceField, StrField
from httpbase.exceptions import SerializationError, NonNullableField
from httpbase.resources import Resource


MockStrField = StrField(label="bar")
MockStrField.to_value = mock.MagicMock(return_value="bar")
MockStrField.value = mock.MagicMock(return_value="bar")


class TestResourceField(TestCase):
    def test_resource_field(self):
        class Parent(Resource):
            foo = ResourceField(label="foo")

        class Child(Resource):
            bar = MockStrField

        value = Child(bar="bar")
        resource = Parent(foo=value)
        self.assertIs(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": {"bar": "bar"}})

    def test_nullable(self):
        class Parent(Resource):
            foo = ResourceField(label="foo", nullable=True)

        resource = Parent()
        self.assertEqual(resource.dict(), {"foo": None})

        class Parent(Resource):
            foo = ResourceField(label="foo")

        with self.assertRaises(NonNullableField):
            Parent(foo=None)

    def test_default(self):
        class Child(Resource):
            bar = MockStrField

        value = Child(bar="bar")

        class Parent(Resource):
            foo = ResourceField(label="foo", default=value)

        resource = Parent()
        self.assertEqual(resource.foo.value.bar.value, value.bar.value)
        self.assertEqual(resource.dict(), {"foo": {"bar": "bar"}})

    def test_validator(self):
        def value_is_resource(value):
            if issubclass(value, Resource):
                return value
            else:
                raise TypeError("not a resource")

        class Parent(Resource):
            foo = ResourceField(label="foo", validator=value_is_resource)

        class Child(Resource):
            bar = MockStrField

        value = Child(bar="bar")

        resource = Parent(foo=value)
        self.assertEqual(resource.dict(), {"foo": {"bar": "bar"}})

        resource = Parent(foo="1234567891011")
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_printable(self):
        class Parent(Resource):
            foo = ResourceField(label="foo", printable=False)

        class Child(Resource):
            bar = MockStrField

        value = Child(bar="bar")

        resource = Parent(foo=value)
        self.assertEqual(resource.dict(), {"foo": {"bar": "bar"}})
        self.assertNotIn(repr(value), repr(resource.foo))

    def test_omit_null(self):
        class Parent(Resource):
            foo = ResourceField(label="foo", nullable=True, omit_null=True)

        resource = Parent()
        self.assertEqual(resource.dict(), {})
