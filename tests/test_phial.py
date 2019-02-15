"""Test the creation of Phial objects."""
from phial import Phial, Router, Response
import pytest
from tests.common import SendMock, receive


def test_constructed_phial_contains_router():
    """Test that the constructed phial contains the same router."""
    router = Router()
    @router.route(r'^/hi/?$')
    def sayhi():
        return "Hello World"
    app = Phial(router=router)
    assert app.router == router


@pytest.mark.asyncio
async def test_end_to_end_async_request():
    """Test that the phial returns an OK response to a request.
    
    Uses an async view function."""
    router = Router()
    @router.route(r'^/$')
    async def index(request):
        return Response("Welcome to the Index")
    app = Phial(router=router)
    request_session = app(
        {
            'type': 'http',
            'method': 'GET',
            'query_string': b'',
            'path': '/'
        }
    )
    mock = SendMock()
    await request_session(receive, mock)
    assert mock.sent
