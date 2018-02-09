from datetime import datetime
import sys
from typing import NamedTuple

from httpbase import Route, HTTPBaseClient, Resource, HTTPResponseCodes, HTTPMethods, Response


class Todo(Resource):
    # Sometimes the Pythonic naming conventions won't match with the service you are calling. This can help.
    _mapped_fields = {"started_on": "startedOn"}

    def __init__(self, title: str, done: bool=False, started_on: int=None, id: int=None):
        self.id = id
        self.title = title
        self.done = done
        if started_on is None:
            started_on = int(datetime.utcnow().timestamp())
        self.started_on = started_on

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)


# You don't have to do this but I prefer to have all the routes in a container
class _Routes(NamedTuple):
    # Basic route. No template variables, no query params
    new_todo: Route = Route("/api/todos", HTTPMethods.POST)
    # Path that needs an id.
    get_todo: Route = Route("/api/todos/{todo_id}", HTTPMethods.GET, vars={"todo_id"})
    # Path that has some query params it will honor
    search_todos: Route = Route("/api/todos/", HTTPMethods.GET, params={"title", "done"})


routes = _Routes()


class TodoClient(HTTPBaseClient):
    # Sometimes you'll need to add some headers that consuming code doesn't know about (or shouldn't know about).
    def _inject_headers(self, req_kwargs: dict) -> dict:
        my_headers = {"Authorization": "Bearer XXXX"}
        if req_kwargs.get("headers"):
            req_kwargs["headers"].update(my_headers)
        else:
            req_kwargs["headers"] = my_headers
        return req_kwargs

    def new_todo(self, todo: Todo) -> Response:
        return self._make_request(routes.new_todo, data=todo.json())

    def get_todo(self, todo_id) -> Response:
        return self._make_request(routes.get_todo, todo_id=todo_id)

    def search_todos(self, **params):
        return self._make_request(routes.search_todos, params=params)


if __name__ == "__main__":
    # Create a client and give the full URL of the service you want to interact with
    client = TodoClient("http://todoservice.com")

    # Create a resource
    todo = Todo("My first Todo")
    response = client.new_todo(todo)

    # Use constants like a civilized person
    if response.status_code == HTTPResponseCodes.INTERNAL_SERVER_ERROR:
        print("they messed up")
        sys.exit(1)
    elif response.status_code == HTTPResponseCodes.BAD_REQUEST:
        print("you messed up")
        sys.exit(1)

    todo2 = Todo.from_dict(response.json())
    response = client.get_todo(todo2.id)

    response = client.search_todos(title="foo")
