import sys
from typing import NamedTuple

from httpbase import Response
from httpbase.client import HTTPBaseClient
from httpbase.constants import HTTPResponseCodes, HTTPMethods
from httpbase.fields import IntField, StrField
from httpbase.resources import Resource
from httpbase.routes import Route


def title_max_length(value):
    if len(value) > 50:
        raise TypeError("title too long")
    return str(value)


class Post(Resource):
    # This field can be null.
    id = IntField(label="id", nullable=True)
    # Sometimes the Pythonic naming conventions won't match with the service you are calling. `label` can help.
    # Set a default value for all instances of this resource
    user_id = IntField(label="userId", default=123)
    # add a callable validator to make sure values conform to any rules the API may have. The callable should take one
    # parameter, value, and return a JSON serializable value if it's valid or raise a ``TypeError``.
    title = StrField(label="title", validator=title_max_length)
    body = StrField(label="body")


# You don't have to do this but I prefer to have all the routes in a container
class _Routes(NamedTuple):
    # Basic route. No template variables, no query params
    new_post: Route = Route("/posts", HTTPMethods.POST)
    # Path that needs an id.
    get_post: Route = Route("/posts/{post_id}", HTTPMethods.GET)
    # Path that has some query params it will honor
    search_posts: Route = Route("/posts", HTTPMethods.GET, params={"userId"})


routes = _Routes()


class PostClient(HTTPBaseClient):
    # Sometimes you'll need to add some headers that consuming code doesn't know about (or shouldn't know about).
    def _inject_headers(self, req_kwargs: dict) -> dict:
        my_headers = {"Authorization": "Bearer XXXX"}
        if req_kwargs.get("headers"):
            req_kwargs["headers"].update(my_headers)
        else:
            req_kwargs["headers"] = my_headers
        return req_kwargs

    def new_post(self, post: Post) -> Response:
        return self._make_request(routes.new_post, data=post.json())

    def get_post(self, post_id) -> Response:
        return self._make_request(routes.get_post, post_id=post_id)

    def search_posts(self, **params) -> Response:
        return self._make_request(routes.search_posts, params=params)


if __name__ == "__main__":
    # Create a client and give the full URL of the service you want to interact with
    client = PostClient("https://jsonplaceholder.typicode.com")

    # Create a resource
    post = Post(title="My first Post", body="Some body text", user_id=1)
    response = client.new_post(post)
    # Use convenience methods for checking HTTP response code class.
    if HTTPResponseCodes.is_5xx_code(response.status_code):
        print("they messed up")
        sys.exit(1)
    elif HTTPResponseCodes.is_4xx_code(response.status_code):
        # check specific codes, use constants like a civilized persons.
        if response.status_code == HTTPResponseCodes.NOT_FOUND:
            print("NOT FOUND!")
            sys.exit(1)
        elif response.status_code == HTTPResponseCodes.BAD_REQUEST:
            print("BAD REQUEST!")
            sys.exit(1)
    elif HTTPResponseCodes.is_2xx_code(response.status_code):
        print(response.json())

    response = client.get_post(1)
    print(response.json())
