"""Common testing utilities."""


class SendMock:
    """A mock of the `send` object."""
    def __init__(self):
        self.sent = []

    async def __call__(self, data):
        """Store the sent data."""
        print(data)
        self.sent.append(data)


async def receive() -> dict:
    """Mock of the receive callback."""
    return {
        'type': 'http.request',
        'body': b'',
        'more_body': False,
    }
