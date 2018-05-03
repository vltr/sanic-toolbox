import binascii
import os

from sanic import Sanic
from sanic.response import text

import ujson
from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy

# DO NOT USE THIS IN PRODUCTION, THIS IS JUST A PROOF OF CONCEPT


class MyInterface:

    def __init__(self):
        self.session_store = dict()

    async def open(self, request) -> dict:
        sid = request.headers.get("sid", None)

        if sid is None:
            sid = binascii.hexlify(os.urandom(32)).decode("utf-8")
            request.headers["sid"] = sid

        if sid not in self.session_store:
            self.session_store[sid] = ujson.dumps({"sid": sid})
        session_dict = ujson.loads(self.session_store[sid])
        request["session"] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        if "session" not in request:
            return

        sid = request["session"]["sid"]
        val = ujson.dumps(request["session"])
        self.session_store[sid] = val
        response.headers["sid"] = sid


class SanicSessionView(make_lazy_view("sanic_session")):
    app = ObjectProxy()
    interface = MyInterface()

    @lazy_decorate(app.middleware("request"))
    async def add_session_to_request(self, request):
        await self.interface.open(request)

    @lazy_decorate(app.middleware("response"))
    async def save_session(self, request, response):
        await self.interface.save(request, response)


def test_sanic_session_like_plugin():
    app = Sanic(name="my-sanic-session")

    SanicSessionView.register(app=app)

    @app.route("/")
    async def index(request):
        if not request["session"].get("foo"):
            request["session"]["foo"] = 0
        request["session"]["foo"] += 1
        return text(request["session"]["foo"])

    request, response = app.test_client.get("/")
    sid = response.headers.get("sid")
    assert response.text == "1"

    request, response = app.test_client.get("/", headers={"sid": sid})
    assert response.text == "2"

    custom_sid = binascii.hexlify(os.urandom(32)).decode("utf-8")

    request, response = app.test_client.get("/", headers={"sid": custom_sid})
    assert response.text == "1"

    request, response = app.test_client.get("/", headers={"sid": custom_sid})
    assert response.text == "2"
