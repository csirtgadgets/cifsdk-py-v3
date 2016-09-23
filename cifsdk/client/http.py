import logging
import requests
import time
import json
from cifsdk.exceptions import AuthError, TimeoutError
from cifsdk.constants import VERSION
from pprint import pprint
import zlib
from base64 import b64decode
import binascii
from cifsdk.client.plugin import Client

logger = logging.getLogger(__name__)


class HTTP(Client):

    def __init__(self, remote, token, proxy=None, timeout=300, verify_ssl=True, **kwargs):
        super(HTTP, self).__init__(remote, token, **kwargs)

        self.proxy = proxy
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.session = requests.Session()
        self.session.headers["Accept"] = 'application/vnd.cif.v3+json'
        self.session.headers['User-Agent'] = 'cifsdk-py/{}'.format(VERSION)
        self.session.headers['Authorization'] = 'Token token=' + self.token
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['Accept-Encoding'] = 'gzip'

    def _get(self, uri, params={}):
        if not uri.startswith('http'):
            uri = self.remote + uri
        body = self.session.get(uri, params=params, verify=self.verify_ssl)

        if body.status_code > 303:
            err = 'request failed: %s' % str(body.status_code)
            logger.error(err)

            if body.status_code == 401:
                raise AuthError('invalid token')
            elif body.status_code == 404:
                err = 'not found'
                raise RuntimeError(err)
            elif body.status_code == 408:
                raise TimeoutError('timeout')
            else:
                try:
                    err = json.loads(body.content).get('message')
                    raise RuntimeError(err)
                except ValueError as e:
                    err = body.content
                    logger.error(err)
                    raise RuntimeError(err)

        data = body.content
        try:
            data = zlib.decompress(b64decode(data))
        except (TypeError, binascii.Error) as e:
            pass
        except Exception as e:
            pass

        msgs = json.loads(data.decode('utf-8'))

        if isinstance(msgs['data'], list):
            for m in msgs['data']:
                if m.get('message'):
                    try:
                        m['message'] = b64decode(m['message'])
                    except Exception as e:
                        pass
        return msgs

    def _post(self, uri, data):
        if type(data) == dict:
            data = json.dumps(data)

        # TODO -- compression?
        body = self.session.post(uri, data=data)

        if body.status_code > 303:
            err = 'request failed: %s' % str(body.status_code)
            logger.debug(err)
            err = body.content

            if body.status_code == 401:
                raise AuthError('unauthorized')
            elif body.status_code == 404:
                err = 'not found'
                raise RuntimeError(err)
            elif body.status_code == 408:
                raise TimeoutError('timeout')
            else:
                try:
                    err = json.loads(err.decode('utf-8')).get('message')
                except ValueError as e:
                    err = body.content

                logger.error(err)
                raise RuntimeError(err)

        logger.debug(body.content.decode('utf-8'))
        body = json.loads(body.content.decode('utf-8'))
        return body

    def _delete(self, uri, data):
        body = self.session.delete(uri, data=json.dumps(data))

        if body.status_code > 303:
            err = 'request failed: %s' % str(body.status_code)
            logger.debug(err)
            err = body.content

            if body.status_code == 401:
                raise AuthError('unauthorized')
            elif body.status_code == 404:
                err = 'not found'
                raise RuntimeError(err)
            else:
                try:
                    err = json.loads(err).get('message')
                except ValueError as e:
                    err = body.content

                logger.error(err)
                raise RuntimeError(err)

        logger.debug(body.content)
        body = json.loads(body.content)
        return body

    def _patch(self, uri, data):
        body = self.session.patch(uri, data=json.dumps(data))

        if body.status_code > 303:
            err = 'request failed: %s' % str(body.status_code)
            logger.debug(err)
            err = body.content

            if body.status_code == 401:
                raise AuthError('unauthorized')
            elif body.status_code == 404:
                err = 'not found'
                raise RuntimeError(err)
            else:
                try:
                    err = json.loads(err).get('message')
                except ValueError as e:
                    err = body.content

                logger.error(err)
                raise RuntimeError(err)

        logger.debug(body.content)
        body = json.loads(body.content)
        return body

    def indicators_search(self, filters):
        rv = self._get('/search', params=filters)
        return rv['data']

    def indicators_create(self, data):
        data = str(data).encode('utf-8')

        uri = "{0}/indicators".format(self.remote)
        logger.debug(uri)
        rv = self._post(uri, data)
        return rv["data"]

    def feed(self, filters):
        rv = self._get('/feed', params=filters)
        return rv['data']

    def ping(self, write=False):
        t0 = time.time()

        uri = '/ping'
        if write:
            uri = '/ping?write=1'

        rv = self._get(uri)

        if rv:
            rv = (time.time() - t0)
            logger.debug('return time: %.15f' % rv)

        return rv

    def tokens_search(self, filters):
        rv = self._get('{}/tokens'.format(self.remote), params=filters)
        return rv['data']

    def tokens_delete(self, data):
        rv = self._delete('{}/tokens'.format(self.remote), data)
        return rv['data']

    def tokens_create(self, data):
        logger.debug(data)
        rv = self._post('{}/tokens'.format(self.remote), data)
        return rv['data']

    def tokens_edit(self, data):
        rv = self._patch('{}/tokens'.format(self.remote), data)
        return rv['data']

Plugin = HTTP
