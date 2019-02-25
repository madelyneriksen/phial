"""Test the creation of Phial objects."""
# TODO: Create tests for malformed or incomplete headers.
import pytest
from phial import Phial, Router, Response
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
            'path': '/',
            'headers': [],
        }
    )
    mock = SendMock()
    await request_session(receive, mock)
    assert mock.sent
    assert mock.sent[0]['status'] == 200
    assert mock.sent[1]['body'] == b"Welcome to the Index"


@pytest.mark.asyncio
async def test_sync_request_fails():
    """Test that syncronous requests fail and return a 500 error."""
    router = Router()
    @router.route(r'^/$')
    def index(request):
        return Response("Welcome to the Index")
    app = Phial(router=router)
    request_session = app(
        {
            'type': 'http',
            'method': 'GET',
            'query_string': b'',
            'path': '/',
            'headers': []
        }
    )
    mock = SendMock()
    await request_session(receive, mock)
    assert mock.sent[0]['status'] == 500


@pytest.mark.asyncio
async def test_route_not_found():
    """Test that syncronous requests fail and return a 500 error."""
    router = Router()
    app = Phial(router=router)
    request_session = app(
        {
            'type': 'http',
            'method': 'GET',
            'query_string': b'',
            'path': '/hello',
            'headers': []
        }
    )
    mock = SendMock()
    await request_session(receive, mock)
    assert mock.sent[0]['status'] == 404

@pytest.mark.asyncio
async def test_post_multipart_form_file_uploads():
    """Test that posted multipart file uploads have the filename."""
    router = Router()
    @router.route(r'^/$')
    async def echo_post(request):
        file = request.POST.get('upload')
        assert file
        return Response(file.file_name)

    async def mock_form_multipart():
        return {
            'type': 'http.request',
            'body': bytes('--boundary\n'
                          'Content-Disposition: form-data; name="upload"; filename="hello.txt"\n\n'
                          'hello\n'
                          '--boundary--',
                          "utf-8"),
            "more_body": False,
        }

    app = Phial(router=router)
    request_session = app(
        {
            'type': 'http',
            'method': 'POST',
            'query_string': b'',
            'path': '/',
            'headers': [
                [
                    b'content-type',
                    b'multipart/form-data; boundary=boundary'
                ],
            ]
        }
    )
    mock = SendMock()
    await request_session(mock_form_multipart, mock)
    assert mock.sent[0]['status'] == 200
    assert mock.sent[1]['body'] == b'hello.txt'
