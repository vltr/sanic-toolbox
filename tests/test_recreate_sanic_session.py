import binascii
import os

import pytest
from sanic import Sanic
from sanic.response import text

import ujson
from sanic_toolbox import lazyapp


# DO NOT USE THIS IN PRODUCTION, THIS IS JUST A PROOF OF CONCEPT


class MyInterface:

    def __init__(self):
        self.session_store = dict()

    async def open(self, request) -> dict:
        sid = request.headers.get('sid', None)

        if sid is None:
            sid = binascii.hexlify(os.urandom(32)).decode('utf-8')
            request.headers['sid'] = sid

        if sid not in self.session_store:
            self.session_store[sid] = ujson.dumps({'sid': sid})
        session_dict = ujson.loads(self.session_store[sid])
        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        if 'session' not in request:
            return

        sid = request['session']['sid']
        val = ujson.dumps(request['session'])
        self.session_store[sid] = val
        response.headers['sid'] = sid


@pytest.fixture
def sanic_session():
    plugin = lazyapp()
    interface = MyInterface()

    @plugin.middleware('request')
    async def add_session_to_request(request):
        await interface.open(request)

    @plugin.middleware('response')
    async def save_session(request, response):
        await interface.save(request, response)

    yield plugin


def test_sanic_session_like_plugin(sanic_session):
    app = sanic_session(Sanic(name='my-sanic-session'))

    @app.route('/')
    async def index(request):
        if not request['session'].get('foo'):
            request['session']['foo'] = 0
        request['session']['foo'] += 1
        return text(request['session']['foo'])

    request, response = app.test_client.get('/')
    sid = response.headers.get('sid')
    assert response.text == '1'

    request, response = app.test_client.get('/', headers={'sid': sid})
    assert response.text == '2'

    custom_sid = binascii.hexlify(os.urandom(32)).decode('utf-8')

    request, response = app.test_client.get('/', headers={'sid': custom_sid})
    assert response.text == '1'

    request, response = app.test_client.get('/', headers={'sid': custom_sid})
    assert response.text == '2'
