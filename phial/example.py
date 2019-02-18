# pylint: disable=unused-argument, invalid-name
"""An example app using the Phial framework."""
from phial import Router, Phial, Response

ROUTER = Router()

@ROUTER.route(r'^/$')
async def say_hello(request):
    """Say hello to the world!!!"""
    return Response("Hello World", content_type="text/plain")

@ROUTER.route(r'^/(?P<name>[\w]*)/?$')
async def hello_name(request, name: str):
    """Say hello based on names."""
    return Response(f"Hello {name}", content_type="text/plain")

app = Phial(router=ROUTER)
