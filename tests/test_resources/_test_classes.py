from httpbase.fields import StrField, ResourceField, MapField
from httpbase.resources import Resource


class PostResource(Resource):
    author = ResourceField()
    body = StrField()
    metadata = MapField(label="metaData")


class AuthorResource(Resource):
    profile = ResourceField()
    name = StrField()


class ProfileResource(Resource):
    email = StrField()
