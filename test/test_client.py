import py.test

from cifsdk.client import Client


def test_cli():
    cli = Client('https://localhost:3000', 12345)
    assert cli.remote == 'https://localhost:3000'

    from pprint import pprint
    pprint(cli)
