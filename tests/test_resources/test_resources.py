from datetime import datetime
import json
from unittest import TestCase

from httpbase.resources import Resource
from httpbase.fields import IntField, ResourceField, ListField


class FlatResource(Resource):
        foo_id = IntField(label="fooId", nullable=True, default=123)


class NestedResource(Resource):
        bar_id = IntField(label="bar_id")
        bar = ResourceField(label="bar")


class ComplexResource(Resource):
        bar = IntField(label="bar", nullable=True, default=123)
        foo = ListField(label="foo", nullable=True, default=["abc", "123", "def"])
        baz = ResourceField(label="baz", nullable=True, default=FlatResource())
        qux = ResourceField(label="qux", nullable=True, default=NestedResource(bar_id=456, bar=FlatResource(foo_id=456)))


class TestResource(TestCase):
    def setUp(self):
        self.pk = 123

    def test_dict(self):
        expected = {"fooId": self.pk}
        resource = FlatResource(foo_id=self.pk)
        actual = resource.dict()
        self.assertEqual(expected, actual)
        self.assertFalse(resource.errors)

    def test_nested_dict(self):
        expected = {"bar_id": self.pk, "bar": {"fooId": self.pk}}
        resource = NestedResource(bar_id=self.pk, bar=FlatResource())
        actual = resource.dict()
        self.assertEqual(expected, actual)
        self.assertFalse(resource.errors)

    def test_dict_finds_errors(self):
        unsafe_value = datetime.utcnow()
        expected = {"bar_id": self.pk}
        resource = NestedResource(bar_id=self.pk, bar=unsafe_value)
        actual = resource.dict()
        self.assertEqual(expected, actual)
        self.assertTrue(resource.errors)

    def test_dict_can_handle_complex_resources(self):
        expected = {
            "bar": 123,
            "foo": ["abc", "123", "def"],
            "baz": {
                "fooId": 123,
            },
            "qux": {
                "bar_id": 456,
                "bar": {
                    "fooId": 456
                }
            }
        }
        resource = ComplexResource()
        actual = resource.dict()
        self.assertEqual(expected, actual)

    def test_json_raises(self):
        unsafe_value = datetime.utcnow()
        resource = NestedResource(bar_id=self.pk, bar=unsafe_value)
        with self.assertRaises(resource.SerializationError):
            resource.json()

    def test_json(self):
        expected = json.dumps({
            "bar": 123,
            "foo": ["abc", "123", "def"],
            "baz": {
                "fooId": 123,
            },
            "qux": {
                "bar_id": 456,
                "bar": {
                    "fooId": 456
                }
            }
        })
        resource = ComplexResource()
        actual = resource.json()
        self.assertEqual(expected, actual)

    def test_use_labels(self):
        class Parent(Resource):
            child = ResourceField()

        class Child(Resource):
            user_id = IntField(label="userId")

        resource = Parent(child=Child(user_id=123))
        self.assertIn("userId", resource.dict()["child"])
        self.assertIn("user_id", resource.dict(use_labels=False)["child"])
