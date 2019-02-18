Phial - A Simple ASGI Framework
=====

Phial is an async micro-framework for the web written in Python. Created as an educational project, I wanted a better understanding of how async programming works in Python. Additionally, I wanted a chance to work closer to the actual HTTP protocol and understand more about the web.

I took heavy inspiration from the [Bottle](https://bottlepy.org/docs/dev/) framework, in both philosophy and code. Disregarding tests, the source code for Phial fits in one file and can easily be read in an afternoon.

## Using Phial

**Note:** Phial isn't ready for use in production!

Creating a "Hello, world!" in Phial is simple, it should look familiar if you have ever used Flask, Bottle, or another micro-framework:

```python
# hello.py
from phial import Router, Phial, Response

ROUTER = Router()

@ROUTER.route(r'^/$')
async def hello(request):
    return Response("Hello World", content_type="text/plain")

app = Phial(router=ROUTER)
```

Run this file `hello.py` using an ASGI server like [Uvicorn](https://www.uvicorn.org/):

```bash
uvicorn hello:app
```

## Running Tests

After cloning the repo, install the development packages from `requirements.dev.txt`:

```bash
pip install -r requirements.dev.txt
```

Tests are run with the `pytest` command and framework.

## License

* MIT License
