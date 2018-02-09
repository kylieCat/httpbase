from datetime import datetime
from unittest import TestCase

from httpbase.resources import Resource


class FlatResource(Resource):
    _mapped_fields = {"foo_id": "fooId"}

    def __init__(self, foo_id):
        self.foo_id = foo_id


class NestedResource(Resource):
    def __init__(self, bar_id, bar):
        self.bar_id = bar_id
        self.bar = FlatResource(bar)


class ComplexResource(Resource):
    def __init__(self):
        self.bar = 123
        self.foo = ["abc", 123, (1, 2, 3)]
        self.baz = FlatResource(123)
        self.qux = NestedResource(456, "def")


class TestResource(TestCase):
    def setUp(self):
        self.pk = 123

    def test_dict(self):
        expected = {"fooId": self.pk}
        resource = FlatResource(self.pk)
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)
        self.assertFalse(errors)

    def test_nested_dict(self):
        expected = {"bar_id": self.pk, "bar": {"fooId": self.pk}}
        resource = NestedResource(self.pk, self.pk)
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)
        self.assertFalse(errors)

    def test_dict_finds_errors(self):
        unsafe_value = datetime.utcnow()
        expected = {"bar_id": self.pk}
        resource = NestedResource(self.pk, unsafe_value)
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)
        self.assertTrue(errors)

    def test_dict_can_handle_sequences(self):
        expected = {"fooId": [1, 2, 3]}
        resource = FlatResource([1, 2, 3])
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)

        expected = {"fooId": [1, 2, 3]}
        resource = FlatResource((1, 2, 3))
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)

    def test_dict_can_handle_complex_resources(self):
        expected = {
            "bar": 123,
            "foo": ["abc", 123, [1, 2, 3]],
            "baz": {
                "fooId": 123,
            },
            "qux": {
                "bar_id": 456,
                "bar": {
                    "fooId": "def"
                }
            }
        }
        resource = ComplexResource()
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)

    def test_json(self):
        unsafe_value = datetime.utcnow()
        resource = NestedResource(self.pk, unsafe_value)
        with self.assertRaises(resource.SerializationError):
            resource.json()

