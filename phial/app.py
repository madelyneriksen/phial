import asyncio
import re
import functools
from urllib.parse import parse_qs
from types import FunctionType


class Router:
    """Route different matching string patterns to different urls."""
    def __init__(self):
        self.routes = []

    def add_route(self, route: str, view: FunctionType):
        """Add a route. Compiles a regex string and stores it with a tuple.

        Eventually, this should use prefixes so we can more effectively search
        through paths. As it stands, finding a path will be O(n)."""
        self.routes.append(
            (re.compile(route), view)
        )

    def route(self, route: str):
        """Decorator for adding a route to the router.

        This lets the user add routes pretty easily from Python code
        like this:

        @router.route(r'^/mypath$')
        def mypath:
            ...
            return response
        """
        def decorator(view):
            self.add_route(route, view)
            return view
        return decorator

    def dispatch(self, path: str) -> FunctionType:
        """Search for a stored route that matches the given path."""
        for route, view in self.routes:
            match = route.search(path)
            if match:
                return view, match.groupdict()
        raise Exception("Route Not Found.")


class Request:
    """Represents an incoming HTTP request from the ASGI server.

    Handles storing get parameters, the request body,
    and giving view function informations on the context they are
    being called.
    """
    def __init__(self, scope, resolved):
        self._scope = scope
        self._body = resolved
        self.path = scope['path']
        method = scope.get('method', 'GET')
        if method == 'GET':
            self.build_get_params()

    def build_get_params(self):
        """Construction of more advanced parts of a request."""
        self.GET = {}
        qs = parse_qs(self._scope['query_string'].decode('utf-8'))
        self.GET.update(qs)


class Phial:
    """A Phial webserver class.

    When called, returns a callback function that the ASGI server can use,
    while still having access to the parent Phial class.

    Arguments:
        router: a Router instance
    """
    def __init__(self, router=Router()):
        self.router = router

    def __call__(self, scope):
        """The ASGI callback handler."""
        async def callback(receive, send):
            if scope['type'] == 'http':
                await self.handle_http(receive, send, scope)

        return callback

    async def handle_http(self, receive, send, scope):
        """HTTP Handler."""
        resolved = await receive()
        request = Request(scope, resolved)
        view, url_params = self.router.dispatch(request.path)
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain']
            ],
        })
        response = await view(request, **url_params)
        await send({
            'type': 'http.response.body',
            'body': response,
        })
