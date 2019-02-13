from phial import Router, Phial

ROUTER = Router()

@ROUTER.route(r'^/?$')
async def say_hello():
    return b"Hello World"

app = Phial(router=ROUTER)
