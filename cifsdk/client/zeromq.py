import time
import json
from cifsdk.client import Client
from cifsdk.exceptions import AuthError, CIFConnectionError, TimeoutError, InvalidSearch

from pprint import pprint

import zmq

SNDTIMEO = 30000
RCVTIMEO = 30000
LINGER = 3
ENCODING_DEFAULT = "utf-8"
SEARCH_LIMIT = 100
RETRIES = 5
RETRY_SLEEP = 5


class ZMQ(Client):
    def __init__(self, remote, token):
        super(ZMQ, self).__init__(remote, token)

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.RCVTIMEO = RCVTIMEO
        self.socket.SNDTIMEO = SNDTIMEO
        self.socket.setsockopt(zmq.LINGER, LINGER)

        self.logger.debug('token: {}'.format(token))

    def _recv(self):
        mtype, data = self.socket.recv_multipart()
        data = json.loads(data)

        if data.get('status') == 'success':
            return data.get('data')
        elif data.get('message') == 'unauthorized':
            raise AuthError('unauthorized')
        elif data.get('message') == 'invalid search':
            raise InvalidSearch('invalid search')
        else:
            self.logger.error(data.get('status'))
            self.logger.error(data.get('data'))
            raise RuntimeError(data.get('message'))

    def _send(self, mtype, data='[]', retries=RETRIES, timeout=SNDTIMEO, retry_sleep=RETRY_SLEEP):
        self.logger.debug('connecting to {0}'.format(self.remote))
        self.logger.debug("mtype {0}".format(mtype))

        self.socket.connect(self.remote)

        # zmq requires .encode
        self.logger.debug("sending")

        sent = False
        while not sent and retries > 0:
            try:
                self.socket.send_multipart([self.token.encode(ENCODING_DEFAULT),
                                            mtype.encode(ENCODING_DEFAULT),
                                            data.encode(ENCODING_DEFAULT)])
                sent = True
            except zmq.error.Again:
                self.logger.warning('timeout... retrying in 5s')
                retries -= 1
                time.sleep(retry_sleep)

        if not sent:
            m = 'unable to connect to remote: {}'.format(self.remote)
            self.logger.warn(m)
            raise TimeoutError(m)

        self.logger.debug("receiving")
        retries = RETRIES
        while retries > 0:
            try:
                return self._recv()
            except zmq.error.Again:
                self.logger.warn('timeout trying to receive, retrying...')
                retries -= 1

        raise TimeoutError('timeout waiting for: {}'.format(self.remote))

    def _handle_message_fireball(self, s, e):
        self.logger.debug('message recieved')
        m = s.recv_multipart()

        self.logger.debug(m)

        null, mtype, data = m

        data = json.loads(data)

        self.response.append(data)

        self.num_responses -= 1
        self.logger.debug('num responses remaining: %i' % self.num_responses)
        if self.num_responses == 0:
            self.logger.debug('finishing up...')
            self.loop.stop()

    def _send_fireball_timeout(self):
        self.logger.warn('timeout')
        self.loop.stop()
        raise TimeoutError('timeout')

    def _send_fireball(self, mtype, data):
        if len(data) < 3:
            self.logger.error('no data to send')
            return []

        self.logger.debug('connecting to {0}'.format(self.remote))
        self.logger.debug("mtype {0}".format(mtype))
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(self.remote)

        from zmq.eventloop.ioloop import IOLoop
        self.loop = IOLoop.instance()
        timeout = time.time() + SNDTIMEO
        self.loop.add_timeout(timeout, self._send_fireball_timeout)
        self.response = []

        self.loop.add_handler(self.socket, self._handle_message_fireball, zmq.POLLIN)

        data = json.loads(data)

        if not isinstance(data, list):
            data = [data]

        self.num_responses = len(data)
        self.logger.debug('responses: %i' % self.num_responses)

        # zmq requires .encode
        for d in data:
            d = json.dumps(d)
            self.socket.send_multipart(['', self.token.encode(ENCODING_DEFAULT),
                                        mtype.encode(ENCODING_DEFAULT),
                                        d.encode(ENCODING_DEFAULT)])

        self.logger.debug("starting loop to receive")
        self.loop.start()

        return self.response

    def test_connect(self):
        try:
            self.socket.RCVTIMEO = 5000
            self.ping()
            self.socket.RCVTIMEO = RCVTIMEO
        except zmq.error.Again:
            return False

        return True

    def ping(self, write=False):
        if write:
            return self._send('ping_write')
        else:
            return self._send('ping')

    def indicators_search(self, filters):
        rv = self._send('indicators_search', json.dumps(filters))
        return rv

    def indicators_create(self, data, fireball=False):
        if isinstance(data, dict):
            data = self._kv_to_indicator(data)

        if not isinstance(data, str):
            data = str(data)

        if fireball:
            self.logger.info('using fireball mode')
            data = self._send_fireball("indicators_create", data)
        else:
            data = self._send('indicators_create', data)

        return data

    def tokens_search(self, filters={}):
        return self._send('tokens_search', json.dumps(filters))

    def tokens_create(self, data):
        return self._send('tokens_create', data)

    def tokens_delete(self, data):
        return self._send('tokens_delete', data)

    def tokens_edit(self, data):
        return self._send('tokens_edit', data)

Plugin = ZMQ
