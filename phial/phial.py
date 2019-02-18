import asyncio
import re
from urllib.parse import parse_qs
from types import FunctionType


async def default404(request, error=''):
    """Default 404 handler."""
    return Response(str(error), status=404)


async def default500(request, error=''):
    """Default 404 handler."""
    return Response(str(error), status=500)


class Router:
    """Route different matching string patterns to different urls."""
    def __init__(self, view_404=None, view_500=None):
        self.routes = {}
        self.handler404 = view_404 if view_404 else default404
        self.handler500 = view_500 if view_500 else default500

    def add_route(self, route: str, view: FunctionType):
        """Add a route. Compiles a regex string and stores it with a tuple.

        Eventually, this should use prefixes so we can more effectively search
        through paths. As it stands, finding a path will be O(n)."""
        self.routes[route] = [re.compile(route), view]

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
        for route in self.routes:
            regex = self.routes[route][0]
            match = regex.search(path)
            if match:
                view = self.routes[route][1]
                return view, match.groupdict()
        return self.handler404, {"error": "Path {} Not Found".format(path)}


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


class Response:
    """A response object. Returned by a view."""
    def __init__(self, body, status=200, content_type='text/html',
                 extra_headers=None):
        self.body = body.encode('utf-8')
        self.status = status
        self.content_type = content_type.encode('utf-8')
        self.headers = extra_headers if extra_headers else []

    async def send_response(self, send):
        """Send an http response."""
        await send({
            'type': 'http.response.start',
            'status': self.status,
            'headers': [
                [b'content_type', self.content_type],
                *self.headers
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': self.body,
        })


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
        try:
            response = await view(request, **url_params)
        except Exception as error:
            response = await self.router.handler500(request, error=error)
        await response.send_response(send)