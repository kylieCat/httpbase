import requests

from .client import HTTPBaseClient
from .constants import HTTPMethods, HTTPResponseCodes
from .resources import Resource
from .routes import Route

# Alias the Response class form requests so it can be used as a type hint with having to import form a dependency
Response = requests.Response
