from datetime import datetime
import sys
from typing import NamedTuple

from httpbase import Route, HTTPBaseClient, Resource, HTTPResponseCodes, HTTPMethods, Response


class Post(Resource):
    # Sometimes the Pythonic naming conventions won't match with the service you are calling. This can help.
    _mapped_fields = [("user_id", "userId")]

    def __init__(self, title: str, body: str, user_id: int, id: int=None, **kwargs):
        # Don't forget to call super!
        super().__init__()
        self.id = id
        self.user_id = user_id
        self.title = title
        self.body = body


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

    def search_posts(self, **params):
        return self._make_request(routes.search_posts, params=params)


if __name__ == "__main__":
    # Create a client and give the full URL of the service you want to interact with
    client = PostClient("https://jsonplaceholder.typicode.com")

    # Create a resource
    todo = Post("My first Post", "Some body text", 1)
    response = client.new_post(todo)
    print(response.json())

    # Use constants like a civilized person
    if response.status_code == HTTPResponseCodes.INTERNAL_SERVER_ERROR:
        print("they messed up")
        sys.exit(1)
    elif response.status_code == HTTPResponseCodes.BAD_REQUEST:
        print("you messed up")
        sys.exit(1)

    response = client.get_post(1)
    print(response.json())
