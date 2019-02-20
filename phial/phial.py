# pylint: disable=too-few-public-methods, attribute-defined-outside-init
"""A tiny, async webframework written in Python3."""
import re
import cgi
from io import BytesIO
from urllib.parse import parse_qs
from types import FunctionType


async def default404(_, error=''):
    """Default 404 handler."""
    return Response(str(error), status=404)


async def default500(_, error=''):
    """Default 404 handler."""
    return Response(str(error), status=500)


class UploadedFile:
    """A file uploaded through a multipart/form POST request."""
    def __init__(self, file, field_name, file_name, headers):
        self.file = file
        self.field_name = field_name
        self.file_name = file_name
        self.headers = headers


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
        def mypath(request):
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
    @classmethod
    async def create(cls, scope, receive):
        """Async factory method for creating a request object."""
        self = Request()
        self._scope = scope
        self.body = await self.receive_body(receive)
        self.path = scope['path']
        self.method = scope.get('method', 'GET')
        self.headers = {}
        for key, value in scope['headers']:
            key = key.decode('utf-8')
            self.headers[key] = value.decode('utf-8')
        self.content_type = self.headers.get('content-type')
        if self.method == 'GET':
            self.GET = self.build_get_params() #  pylint: disable=invalid-name
        elif self.method == 'POST':
            self.POST = self.build_post_params() #  pylint: disable=invalid-name
        return self

    async def receive_body(self, receive):
        """Load all of the body contained in the request and store it.

        This is based off a similar example from the Uvicorn documentation.
        """
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        return body

    def build_get_params(self):
        """Construction of more advanced parts of a request."""
        get = {}
        query_string = parse_qs(self._scope['query_string'].decode('utf-8'))
        get.update(query_string)
        return get

    def build_post_params(self):
        """Construction of POST parameters and content"""
        post = {}
        # Using the CGI module to parse multipart form data.
        # This section is inspired by similar bottle code.
        if self.content_type.startswith('multipart/'):
            safe_env = {'QUERY_STRING': '', 'REQUEST_METHOD': 'POST'}
            safe_env.update({'CONTENT_TYPE': self.content_type})
            safe_env.update({'CONTENT_LENGTH': self.headers['content-length']})
            cgi_args = dict(
                fp=BytesIO(self.body),
                environ=safe_env,
                keep_blank_values=True
            )
            data = cgi.FieldStorage(**cgi_args)
            data = data.list or []
            for item in data:
                if item.filename:
                    post[item.name] = UploadedFile(item.file, item.name,
                                                   item.filename, item.headers)
                else:
                    post[item.name] = item.value
        return post


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
        request = await Request.create(scope, receive)
        view, url_params = self.router.dispatch(request.path)
        try:
            response = await view(request, **url_params)
        except Exception as error:  # pylint: disable=broad-except
            response = await self.router.handler500(request, error=error)
        await response.send_response(send)
