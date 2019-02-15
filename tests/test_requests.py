"""Tests for the Request class."""
from phial.phial import Request


def test_request_constructs_query_strings():
    """Test that GET requests have properly formed querystrings."""
    scope = {
        'path': '/',
        'method': 'GET',
        'query_string': b'working=yes',
    }
    resolved = {}
    request = Request(scope, resolved)
    assert request.GET['working']
    assert request.GET['working'] == ['yes']
