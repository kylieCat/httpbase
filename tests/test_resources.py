from datetime import datetime
import json
from unittest import TestCase

from httpbase.resources import Resource


class FlatResource(Resource):
    mapped_fields = [("foo_id", "fooId")]

    def __init__(self, foo_id):
        super().__init__()
        self.foo_id = foo_id


class NestedResource(Resource):
    def __init__(self, bar_id, bar):
        super().__init__()
        self.bar_id = bar_id
        self.bar = FlatResource(bar)


class ComplexResource(Resource):
    def __init__(self):
        super().__init__()
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

    def test_serialize_sequence_error_case(self):
        unsafe_value = datetime.utcnow()
        resource = FlatResource(["foo", unsafe_value])
        actual, errors = resource.dict()
        self.assertFalse(actual)
        self.assertTrue(errors)

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

    def test_dict_can_handle_dicts(self):
        expected = {"bar_id": {"pk": self.pk}, "bar": {"fooId": {self.pk: "foo"}}}
        resource = NestedResource({"pk": self.pk}, {self.pk: "foo"})
        actual, errors = resource.dict()
        self.assertEqual(expected, actual)
        self.assertFalse(errors)

    def test_serialize_dict_error_case(self):
        unsafe_value = datetime.utcnow()
        resource = FlatResource({"foo": unsafe_value})
        actual, errors = resource.dict()
        self.assertFalse(actual)
        self.assertTrue(errors)

    def test_json_raises(self):
        unsafe_value = datetime.utcnow()
        resource = NestedResource(self.pk, unsafe_value)
        with self.assertRaises(resource.SerializationError):
            resource.json()

    def test_json(self):
        expected = json.dumps({
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
        })
        resource = ComplexResource()
        actual = resource.json()
        self.assertEqual(expected, actual)

