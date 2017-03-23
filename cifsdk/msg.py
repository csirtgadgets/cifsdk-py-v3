import ujson as json
from pprint import pprint
import msgpack
import logging
from cifsdk.constants import PYVERSION
import os

TRACE = os.environ.get('CIFSDK_CLIENT_MSG_TRACE')
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)

MAP = {
    1: 'ping',
    2: 'ping_write',
    3: 'indicators_create',
    4: 'indicators_search',
    5: 'indicators_delete',
    6: 'tokens_search',
    7: 'tokens_create',
    8: 'tokens_delete',
    9: 'tokens_edit',
}


class Msg(object):

    PING = 1
    PING_WRITE = 2
    INDICATORS_CREATE = 3
    INDICATORS_SEARCH = 4
    INDICATORS_DELETE = 5
    TOKENS_SEARCH = 6
    TOKENS_CREATE = 7
    TOKENS_DELETE = 8
    TOKENS_EDIT = 9

    def __init__(self, *args, **kwargs):
        for k in kwargs:
            if isinstance(kwargs[k], str):
                try:
                    kwargs[k] = kwargs[k].encode('utf-8')
                except UnicodeDecodeError:
                    pass

        self.id = kwargs.get('id')
        self.client_id = kwargs.get('client_id')
        self.mtype = kwargs.get('mtype')
        self.token = kwargs.get('token')
        self.data = kwargs.get('data')
        self.null = ''.encode('utf-8')

    # from str to int
    def mtype_to_int(self, mtype):
        for m in MAP:
            if MAP[m] == mtype:
                return m

    def __repr__(self):
        m = {
            'id': self.id,
            'mtype': self.mtype,
            'token': self.token,
            'data': self.data,
        }

        return json.dumps(m)

    def recv(self, s):
        m = s.recv_multipart()

        if len(m) == 6:
            id, client_id, null, token, mtype, data = m
            mtype = msgpack.unpackb(mtype)
            mtype = MAP[mtype]
            return id, client_id, token.decode('utf-8'), mtype, data.decode('utf-8')

        elif len(m) == 5:
            id, null, token, mtype, data = m
            mtype = msgpack.unpackb(mtype)
            mtype = MAP[mtype]
            return id, token.decode('utf-8'), mtype, data.decode('utf-8')

        elif len(m) == 4:
            id, token, mtype, data = m
            mtype = msgpack.unpackb(mtype)
            mtype = MAP[mtype]
            return id, token.decode('utf-8'), mtype, data.decode('utf-8')

        elif len(m) == 3:
            id, mtype, data = m
            try:
                mtype = msgpack.unpackb(mtype)
                mtype = MAP[mtype]
            except msgpack.exceptions.ExtraData:
                pass
            return id, mtype, data.decode('utf-8')

        else:
            mtype, data = m
            return mtype, data.decode("utf-8")

    def to_list(self):
        m = []
        if self.id:
            m.append(self.id)

        if self.client_id:
            m.append(self.client_id)

        if len(m) > 0:
            m.append(self.null)

        if self.token:
            if isinstance(self.token, str):
                self.token = self.token.encode('utf-8')

            if PYVERSION == 2:
                if isinstance(self.token, unicode):
                    self.token = self.token.encode('utf-8')

            m.append(self.token)

        if self.mtype:
            if isinstance(self.mtype, bytes):
                self.mtype = self.mtype_to_int(self.mtype.decode('utf-8'))

            m.append(msgpack.packb(self.mtype))

        if isinstance(self.data, dict):
            self.data = [self.data]

        if isinstance(self.data, list):
            self.data = json.dumps(self.data)

        if isinstance(self.data, str):
            self.data = self.data.encode('utf-8')

        if PYVERSION == 2:
            if isinstance(self.data, unicode):
                self.data = self.data.encode('utf-8')

        m.append(self.data)
        return m

    def send(self, s):
        m = self.to_list()

        logger.debug('sending...')
        s.send_multipart(m)
