from phial import Router, Phial

ROUTER = Router()

@ROUTER.route(r'^/?$')
async def say_hello(request):
    print(request._scope)
    print(request._body)
    print(request.GET)
    return b"Hello World"

@ROUTER.route(r'^/(?P<name>[\S]*)/?$')
async def hello_name(request, name: str):
    return f"Hello {name}".encode('utf-8')

app = Phial(router=ROUTER)
