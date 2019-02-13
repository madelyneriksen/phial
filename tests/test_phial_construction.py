"""Test the creation of Phial objects."""
from phial import Phial, Router
from phial.app import _Phial


def test_constructed_phial_is_asgiapp():
    """Test that we can construct an ASGI application using the Phial wrapper."""
    router = Router()
    @router.route(r'^/hi/?$')
    def sayhi():
        return "Hello World"
    app = Phial(router=router)
    assert app.router == router
