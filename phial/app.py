import asyncio
import re
import functools
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


class _Phial:
    """The actual Phial class. Wrapped by the callable, `Phial`."""
    def __init__(self, scope, router=Router()):
        self.router = router
        self.scope = scope

    async def __call__(self, receive, send):
        if self.scope['type'] == 'http':
            await self.handle_http(receive, send)

    async def handle_http(self, receive, send):
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain']
            ],
        })
        print(self.scope['path'])
        await send({
            'type': 'http.response.body',
            'body': b'Hello World.'
        })


def Phial(router=None):
    """Constructor for creating a Phial web server.

    While technically a function, it functions more like a class that
    wraps a class (that wraps a callable). Feeds values into a new
    Phial class that gets called by the ASGI server for each request.
    """
    router = router if router else Router()
    app = _Phial
    app.__init__ = functools.partialmethod(app.__init__, router=router)
    return app
