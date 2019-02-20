"""Tests for the Request class."""
import pytest
from phial.phial import Request

@pytest.mark.asyncio
async def test_request_constructs_query_strings():
    """Test that GET requests have properly formed querystrings."""
    scope = {
        'path': '/',
        'method': 'GET',
        'query_string': b'working=yes',
        'headers': [],
    }
    resolved = {}
    request = await Request.create(scope, resolved)
    assert request.GET['working']
    assert request.GET['working'] == ['yes']
