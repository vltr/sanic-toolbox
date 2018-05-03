import binascii
import datetime
import os

from sanic import Sanic
from sanic.response import json

from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy


class MyViewHelper:

    __max_length__ = 32

    def get_random_string(self):
        return binascii.hexlify(os.urandom(self.__max_length__)).decode(
            "utf-8"
        )


class AnotherViewHelper:

    def get_current_time(self):
        return datetime.datetime.utcnow().isoformat()


class MyCustomView(make_lazy_view("MyCustomView", MyViewHelper)):
    app = ObjectProxy()

    @lazy_decorate(app.route("/", methods=["GET"]), app.route("/baz"))
    async def company_list(self, request):
        return json({"hello": "world"})

    @lazy_decorate(app.middleware("response"))
    async def add_sid(self, request, response):
        response.headers.update({"x-sid": self.get_random_string()})


class MyOtherCustomView(
    make_lazy_view("MyOtherCustomView", (MyViewHelper, AnotherViewHelper))
):
    app = ObjectProxy()

    @lazy_decorate(app.route("/", methods=["GET"]), app.route("/baz"))
    async def company_list(self, request):
        return json({"hello": "world"})

    @lazy_decorate(app.middleware("response"))
    async def add_sid_and_ts(self, request, response):
        response.headers.update({"x-sid": self.get_random_string()})
        response.headers.update({"x-ts": self.get_current_time()})


def test_my_custom_view():
    app = Sanic()

    MyCustomView.register(app=app)

    _, response = app.test_client.get("/")

    assert response.status == 200
    assert response.json.get("hello") == "world"
    assert "x-sid" in response.headers
    assert "x-ts" not in response.headers


def test_my_other_view():
    app = Sanic()

    MyOtherCustomView.register(app=app)

    _, response = app.test_client.get("/")

    assert response.status == 200
    assert response.json.get("hello") == "world"
    assert "x-sid" in response.headers
    assert "x-ts" in response.headers
