from aiohttp import TCPConnector

from bolsa.contrib.mixins.singleton import SingletonCreateMixin


class B3HttpClientConnector(SingletonCreateMixin):

    def __init__(self, pool_size=30):
        self.CONNECTOR = TCPConnector(
            limit=pool_size,
            ssl=False
        )

    def get_connector(self):
        return self.CONNECTOR
