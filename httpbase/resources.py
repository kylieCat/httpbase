import copy
import json
from typing import Dict, Union, Mapping, List, Iterator

from .constants import null
from .exceptions import SerializationError
from .fields import Field

# Types for checking
JSON = Union[str, int, float, bool, None, Mapping[str, 'JSON'], List['JSON']]


class ResourceMetaclass(type):
    """Metaclass for ``Resource`` objects. When a class object is constructed at run time this will add any declared
    to a dictionary and set that dictionary as the value for ``_declared_fields``. It will also go up the inheritance
    chain and add any fields from parent ``Resources`` as well.

    This is done so that class instances can make copies of the fields that are assigned to it so that instances of
    the ``Resource`` class don't all share the same fields/values.

    """
    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        fields = [
            (field_name, attrs.pop(field_name)) for field_name, obj in list(attrs.items()) if isinstance(obj, Field)
        ]

        for base in reversed(bases):
            if hasattr(base, '_declared_fields'):
                fields = [
                    (field_name, obj) for field_name, obj
                    in base._declared_fields.items()
                    if field_name not in attrs
                ] + fields

        return dict(fields)

    def __new__(cls, name, bases, attrs):
        attrs['_declared_fields'] = cls._get_declared_fields(bases, attrs)
        return super(ResourceMetaclass, cls).__new__(cls, name, bases, attrs)


class Resource(metaclass=ResourceMetaclass):
    """
    A class the represents a resource in an HTTP API. Subclasses of this class are composed of ``Fields`` which dictate
    how the value within that field will serialized. Resources can contain other resources.

    To deal with the nested nature of these resources this class has some special accessor methods to make traversing
    down deeply nested structures a bit more convenient. They are similar to the ``get()`` on dictionaries and work the
    same way when fetching a value on the parent resource. However they aso support a dotted syntax for traversing
    further down in to nested objects. For example if you had a post resource that had an author and the author had
    a profile that had an email you could access it like so::

        class PostResource(Resource):
            author = ResourceField()


        class AuthorResource(Resource):
            profile = ResourceField()


        class ProfileResource(Resource):
            email = StrField()

        post = PostResource(
            author=AuthorResource(profile=ProfileResource(email="foo@example.com"))
        )
        # to get the value of the StrField ``email``
        post.get_value("author.profile.email")

        # to update the value
        post.update("author.profile.email","new.email@example.com")
    """
    # Expose this exception on this class so calling code can easily use it in ``try/except`` blocks
    SerializationError = SerializationError

    def __init__(self, **kwargs):
        self._errors = {}
        self._fields = {}
        self.parent = None
        for key, field in self.fields.items():
            field._set_parent(self)
            field.set_value(kwargs.get(key))
            setattr(self, key, field)
            if field.label is None:
                field.label = key

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    def fields(self) -> Dict[str, Field]:
        """
        Returns a dictionary where the keys are the attribute name for a field and the value is the ``Field`` object

        Example::

            class PostResource(Resource):
                author_name = StrField()
                title = StrField()
                body = StrField()
                date = DateField()

            post = Post(author_name="Author", title="Post Title", body="...", date=datetime.now())
            print(post.fields())
            {'author_name': <StrField: Author>,
             'body': <StrField: ...>,
             'date': <DateField: 2018-02-17 21:53:44.522987>,
             'title': <StrField: Post Title>}

        Returns:
            dict[str, Field]
        """
        if not self._fields:
            self._fields = {key: value for key, value in copy.deepcopy(self._declared_fields).items()}
        return self._fields

    @property
    def errors(self) -> Dict[str, str]:
        """
        A dictionary containing any errors encountered during serialization. Should be checked prior to suing the
        output of ``dict()``. If this dictionary contains any errors :func:`~httpbase.resources.Resource.json` will
        raise a ``SerializationError``
        """
        return {key: value for key, value in self._errors.items()}

    def dict(self, use_labels: bool=True) -> Dict[str, JSON]:
        """Get a json serializable dictionary

        Returns a dictionary suitable for use with `json.dumps()`. Accepts a keyword argument, ``use_labels``, that
        determines if the attribute name or the ``label`` attribute of the field should be used as the key in the
        resulting dictionary.

        This method will capture most expected exceptions raised during the serialization process and attach them to
        the instance, similar to forms in Django. This method is called by :func:`~httpbase.resources.Resource.json`,
        if there are any errors on the instance JSON serialization will fail. If you are going to use this method
        directly ensure to check for errors prior to using it.

        Example::

            class PostResource(Resource):
                author_name = StrField(label="authorName")
                title = StrField(label="postTitle")
                body = StrField()
                date = DateField()

            post = PostResource(
                author_name="Author", title="Post Title", body="...", date=datetime.now()
            )
            post.dict()
            {'authorName': 'Author',
             'body': '...',
             'date': '2018-02-17 22:08:1518934108',
             'postTitle': 'Post Title'}

            post.dict(use_labels=False)
            {'author_name': 'Author',
             'body': '...',
             'date': '2018-02-17 22:08:1518934108',
             'title': 'Post Title'}

        Keyword Args:
            use_labels: If set to ``False`` the resulting dictionary will use the attribute names of the fields as
                keys in the dictionary. If set to ``True`` the ``label`` attribute of the class will be used. This
                helpful if you want to write the serialized ``Resource`` to a file to loaded again later. That will
                allow use to use the ``Resource(**dict)`` syntax.
        """
        result = {}
        for key, field in self.fields.items():
            try:
                if use_labels:
                    label = field.label
                else:
                    label = key
                if field.omit_null and field.value is null:
                    continue
                elif field.value is null:
                    result[label] = None
                else:
                    result[label] = field.to_value(use_labels=use_labels)
            except (TypeError, AttributeError, ValueError) as err:
                self._errors[key] = f"error from validator: {str(err)}"
        return result

    def json(self, use_labels: bool=True) -> str:
        """
        Get the JSON for an instance.

        Args:
            use_labels: Boolean to determine whether or not the attr name or the label of the ``Field`` should be used.

        Raises:
            SerializationError: Raises a ``SerializationError`` if there are fields that aren't JSON serializable.
        """
        d = self.dict(use_labels=use_labels)
        if self.errors:
            msg = "fields with types {} could not be serialized".format([(k, v) for k, v in self.errors.items()])
            raise SerializationError(msg)
        return json.dumps(d)

    def _traverse_fields(self, path: str) -> Field:
        """
        Method for traversing fields given a dotted path.

        Args:
            path: A dot separated path down the ``Resource`` object.

        Returns:
            Field
        """
        field = self
        levels, target = path.split(".")[:-1], path.split(".")[-1]
        for level in levels:
            field = getattr(field, level).value
        return getattr(field, target, field)

    def get_field(self, path: str) -> Field:
        """
        Given a dot separated path to a field will return the field at the end of the path.

        Example::

            post = PostResource(
                author=AuthorResource(profile=ProfileResource(email="foo@example.com"))
            )
            # This would return the field of the ``email`` attribute on the ``ProfileResource``
            print(post.get_field("author.profile.email"))
            <StrField: foo@example.com>

        Args:
            path: A dot separated path to a field.

        Returns:
            Field
        """
        target = self._traverse_fields(path)
        return target

    def get_value(self, path: str):
        """
        Given a dotted path return the value at the end of that path.

        Example::

            post = PostResource(
                author=AuthorResource(profile=ProfileResource(email="foo@example.com"))
            )
            # This would return the value of the ``email`` field on the ``ProfileResource``
            print(post.get_value("author.profile.email"))
            "foo@example.com"

        Args:
            path: A dot separated path
        """
        target = self._traverse_fields(path)
        return target.value

    def update(self, path: str, value):
        """
        Update the value at given path.

        Example::

            post = PostResource(
                author=AuthorResource(profile=ProfileResource(email="foo@example.com"))
            )
            # This would update the value of the ``email`` field on the ``ProfileResource``
            post.update("author.profile.email", "new.email@example.com")
            print(post.get_value("author.profile.email")
            "new.email@example.com"

        Args:
            path: A dot separated path
            value: A new value
        """
        target = self._traverse_fields(path)
        target.set_value(value)

    def get_label(self, path: str) -> str:
        """
        Get the label for a given path.

        Example::

            post = PostResource(
                author=AuthorResource(profile=ProfileResource(email="foo@example.com"))
            )
            # This would return the label of the ``email`` field on the ``ProfileResource``
            post.get_label("author.profile.email")
            print(post.get_label("author.profile.email")
            "email"

        Args:
            path: A dot separated path.
        """
        target = self._traverse_fields(path)
        return target.label

    def labels(self, path: str="") -> Iterator[str]:
        """
        Yields all the labels for the given resource. If a dotted path is given it will return the labels for the
        resource at the end of that path.

        Example::

            class PostResource(Resource):
                author = ResourceField()
                title = StrField()
                body = StrField()
                date = DateField()

            class AuthorResource(Resource):
                name = StrField(label="authorName")
                post_count = IntField(label="postCount")
                avatar = StrField()

            author = AuthorResource(name="author", post_count=10, avatar="...")
            post = PostResource(
                author=author,
                title="Post Title",
                body="...",
                date=datetime.now(),
            )
            # This would yield the labels of the ``PostResource``
            print(list(post.labels()))
            ['author', 'title', 'body', 'date']
            print(list(post.labels("author")))
            ['authorName', 'postCount', 'avatar']

        Args:
            path: A dot separated path

        Yields:
            str
        """
        target = self._traverse_fields(path)
        if not hasattr(target, "fields"):
            target = target.value
        for key, field in target.fields.items():
            yield field.label
