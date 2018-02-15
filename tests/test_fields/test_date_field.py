from datetime import datetime
from unittest import TestCase

from httpbase.constants import DEFAULT_DATE_FORMAT
from httpbase.fields import DateField
from httpbase.exceptions import SerializationError, NonNullableField
from httpbase.resources import Resource


DATE = datetime(2018, 4, 20, 16, 20)
CUTOFF_DATE = datetime(2018, 4, 15)
FORMATTED_DATE = DATE.strftime(DEFAULT_DATE_FORMAT)


class TestDateField(TestCase):
    def test_date_field(self):
        value = DATE

        class Foo(Resource):
            foo = DateField(label="foo")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": FORMATTED_DATE})

    def test_nullable(self):
        class Foo(Resource):
            foo = DateField(label="foo", nullable=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {"foo": None})

        class Foo(Resource):
            foo = DateField(label="foo")

        with self.assertRaises(NonNullableField):
            Foo(foo=None)

    def test_default(self):
        value = DATE

        class Foo(Resource):
            foo = DateField(label="foo", default=value)

        resource = Foo()
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": FORMATTED_DATE})

    def test_validator(self):
        value = DATE

        def value_in_range(value):
            if value > CUTOFF_DATE:
                return value
            else:
                raise TypeError("date not after cutoff")

        class Foo(Resource):
            foo = DateField(label="foo", validator=value_in_range)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": FORMATTED_DATE})

        resource = Foo(foo="1234567891011")
        with self.assertRaises(SerializationError):
            resource.json()
        self.assertTrue(resource.errors)
        self.assertIn("foo", resource.errors)

    def test_printable(self):
        value = DATE

        class Foo(Resource):
            foo = DateField(label="foo", printable=False)

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": FORMATTED_DATE})
        self.assertNotIn(str(value), repr(resource.foo))

    def test_omit_null(self):
        class Foo(Resource):
            foo = DateField(label="foo", nullable=True, omit_null=True)

        resource = Foo()
        self.assertEqual(resource.dict(), {})

    def test_format(self):
        value = DATE

        class Foo(Resource):
            foo = DateField(label="foo", format="%D")

        resource = Foo(foo=value)
        self.assertEqual(resource.foo.value, value)
        self.assertEqual(resource.dict(), {"foo": DATE.strftime("%D")})
