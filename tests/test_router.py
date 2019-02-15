"""Tests for the router."""
from phial import Router


def test_paths_match_regex_in_router():
    """Test that a simple path matches a router's regex."""
    view = lambda: 'Hello World'
    router = Router()
    router.add_route('^/articles/?$', view)
    result, _ = router.dispatch('/articles/')
    assert result
    assert result() == "Hello World"


def test_paths_return_arguments_from_regex():
    """Test that router paths return the kwargs."""
    view = lambda: 'Hello World'
    router = Router()
    router.add_route('^/articles/(?P<year>[0-9]{4})/?$', view)
    _, kwargs = router.dispatch('/articles/2019/')
    assert kwargs['year'] == '2019'


def test_can_use_decorator_to_add_routes():
    """Test that we can add a route using a decorator."""
    router = Router()
    @router.route('^/articles/?$')
    def articles():
        return "These are articles!"
    assert len(router.routes) == 1
    assert router.dispatch('/articles/')
