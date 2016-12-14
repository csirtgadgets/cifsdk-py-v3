import py.test
from cifsdk.msg import Msg
from pprint import pprint
import zmq
import msgpack


def test_msgs():

    def _send_multipart(m):
        assert msgpack.unpackb(m[0]) == Msg.PING
        assert m[1] == b'[]'

    m = Msg(mtype=Msg.PING, data=[])
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.send_multipart = _send_multipart

    m.send(s)


def test_msgs_recv():

    def _recv_multipart():
        m = Msg(id=msgpack.packb(1234), mtype=Msg.PING, token='token1234', data=[]).to_list()

        return m

    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.recv_multipart = _recv_multipart

    m = Msg().recv(s)

    assert msgpack.unpackb(m[0]) == 1234
    assert m[1] == 'token1234'
    assert m[2] == 'ping'
    assert m[3] == '[]'
