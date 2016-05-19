from pprint import pprint
from cifsdk.client.plugin import Client


class Dummy(Client):

    def __init__(self, remote, token):
        self.remote = remote
        self.token = token

    def ping(self, write=False):
        return True

    def indicators_create(self, data):
        if isinstance(data, dict):
            data = self._kv_to_indicator(data)

        return data

    def indicators_search(self, data):
        return data

Plugin = Dummy