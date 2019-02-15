from phial import Router, Phial, Response

ROUTER = Router()

@ROUTER.route(r'^/?$')
async def say_hello(request):
    print(request._scope)
    print(request._body)
    print(request.GET)
    return Response("Hello World", content_type="text/plain")

@ROUTER.route(r'^/(?P<name>[\S]*)/?$')
async def hello_name(request, name: str):
    return Response(f"Hello {name}", content_type="text/plain")

app = Phial(router=ROUTER)
