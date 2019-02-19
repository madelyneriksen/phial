# pylint: disable=unused-argument, invalid-name
"""An example app using the Phial framework."""
from phial import Router, Phial, Response

router = Router()

@router.route(r'^/$')
async def say_hello(request):
    """Say hello to the world!!!"""
    print(request._scope)
    print(request._body)
    print(request.headers)
    return Response("Hello World", content_type="text/plain")

@router.route(r'^/(?P<name>[\w]*)/?$')
async def hello_name(request, name: str):
    """Say hello based on names."""
    return Response(f"Hello {name}", content_type="text/plain")

app = Phial(router=router)
