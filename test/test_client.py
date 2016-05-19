import py.test


def test_client_dummy():
    from cifsdk.client.dummy import Dummy as Client
    cli = Client('https://localhost:3000', 12345)
    assert cli.remote == 'https://localhost:3000'

    data = {
        'indicator': 'example.com',
        'tags': ['botnet']
    }
    assert cli.indicator_create(data)

    assert cli.indicator_search(data)
