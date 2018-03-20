import binascii
import os

from sanic import Sanic
from sanic.response import text

import ujson
from sanic_toolbox import lazyapp

# DO NOT USE THIS IN PRODUCTION, THIS IS JUST A PROOF OF CONCEPT
#
# With curl, run:
#
# curl -v http://127.0.0.1:8000/
# or
# curl -v -H "Sid: <SID>" http://127.0.0.1:8000/


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


def get_plugin():
    plugin = lazyapp()
    interface = MyInterface()

    @plugin.middleware('request')
    async def add_session_to_request(request):
        await interface.open(request)

    @plugin.middleware('response')
    async def save_session(request, response):
        await interface.save(request, response)

    return plugin


def main():
    sanic_session = get_plugin()
    app = sanic_session(Sanic(name='my-sanic-session'))

    @app.route('/')
    async def index(request):
        if not request['session'].get('foo'):
            request['session']['foo'] = 0
        request['session']['foo'] += 1
        return text(request['session']['foo'])

    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == '__main__':
    main()
