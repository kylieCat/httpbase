from unittest import TestCase

from ._test_classes import PostResource, AuthorResource, ProfileResource


class TestResourceAccessors(TestCase):
    def setUp(self):
        self.profile = ProfileResource(email="foo@example.com")
        self.author = AuthorResource(profile=self.profile, name="author")
        self.post = PostResource(author=self.author, body="This is my post", metadata={"subscribed": True, "popular": False})

    def test_get_field(self):
        target = self.post.get_field("author")
        self.assertIs(target, self.post.author)

        target = self.post.get_field("author.profile")
        self.assertIs(target, self.post.author.value.profile)

        target = self.post.get_field("author.profile.email")
        self.assertIs(target, self.post.author.value.profile.value.email)

    def test_get_value(self):
        target = self.post.get_value("author")
        self.assertIs(target, self.author)

        target = self.post.get_value("author.profile")
        self.assertIs(target, self.profile)

        target = self.post.get_value("author.profile.email")
        self.assertEqual(target, "foo@example.com")

    def test_update(self):
        new_value = "new name"
        self.post.update("author.name", new_value)
        self.assertEqual(self.author.name.value, new_value)

        new_value = {"subscribed": True, "popular": True}
        self.post.update("metadata", new_value)
        self.assertEqual(self.post.metadata.value, new_value)

        new_value = "bar@example.com"
        self.post.update("author.profile.email", new_value)
        self.assertEqual(self.profile.email.value, new_value)

    def test_get_label(self):
        target = self.post.get_label("author")
        self.assertIs(target, "author")

        target = self.post.get_label("author.profile")
        self.assertIs(target, "profile")

        target = self.post.get_label("author.profile.email")
        self.assertEqual(target, "email")

        target = self.post.get_label("metadata")
        self.assertEqual(target, "metaData")

    def test_labels(self):
        target = list(self.post.labels())
        expected = ["author", "body", "metaData"]
        self.assertListEqual(target, expected)

        target = list(self.post.labels("author"))
        expected = ["profile", "name"]
        self.assertEqual(target, expected)

        target = list(self.post.labels("author.profile"))
        expected = ["email"]
        self.assertListEqual(target, expected)
