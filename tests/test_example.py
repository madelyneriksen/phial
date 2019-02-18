"""Test that the packaged example app works."""
import pytest
from phial.example import app
from tests.common import SendMock, receive


@pytest.mark.asyncio
async def test_index_returns_okay():
    """Test the index view."""
    mock = SendMock()
    request_session = app(
        {
            'type': 'http',
            'method': 'GET',
            'query_string': b'',
            'path': '/'
        }
    )
    await request_session(receive, mock)
    assert mock.sent
    assert mock.sent[0]['status'] == 200
    assert mock.sent[1]['body'] == b'Hello World'


@pytest.mark.asyncio
async def test_custom_greeting_returns_okay():
    """Test the named greeting views."""
    mock = SendMock()
    request_session = app(
        {
            'type': 'http',
            'method': 'GET',
            'query_string': b'',
            'path': '/maddie/'
        }
    )
    await request_session(receive, mock)
    assert mock.sent
    assert mock.sent[0]['status'] == 200
    assert mock.sent[1]['body'] == b'Hello maddie'


@pytest.mark.asyncio
async def test_absent_route_404s():
    """Test that missing routes return a proper 404 error."""
    mock = SendMock()
    request_session = app(
        {
            'type': 'http',
            'method': 'GET',
            'query_string': b'',
            'path': '/blog/articles/'
        }
    )
    await request_session(receive, mock)
    assert mock.sent
    assert mock.sent[0]['status'] == 404
    assert mock.sent[1]['body'] == b'Path /blog/articles/ Not Found'
