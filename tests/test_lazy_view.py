import uuid
from sanic.response import json
from sanic import Sanic

from sanic_toolbox import lazy_decorate, get_lazy_view, ObjectProxy


class MyAbstractView(get_lazy_view("my_abstract_view")):
    pass


class MyCustomView(MyAbstractView):
    app = ObjectProxy()

    @lazy_decorate(app.route("/", methods=["GET"]), app.route("/baz"))
    async def company_list(self, request):
        return json({"hello": "world"})

    @lazy_decorate(app.route("/foo", methods=["GET"]))
    @lazy_decorate(app.route("/oof"))
    async def another_test(self, request):
        return json({"another": "test"})

    @lazy_decorate(app.listener("before_server_start"))
    async def simple_assert_check(self, app, loop):
        assert self.app == app


class IgnoredCustomView(MyAbstractView):
    __ignore__ = True
    app = ObjectProxy()

    @lazy_decorate(app.route("/bar", methods=["GET"]))
    async def company_list(self, request):
        return json({"hello": "ignored"})


class AnotherCustomView(get_lazy_view("other_view")):
    app = ObjectProxy()

    @lazy_decorate(app.middleware)
    async def create_request_id(self, request):
        request["request_id"] = uuid.uuid4()

    @lazy_decorate(app.middleware("response"))
    async def attach_request_id(self, request, response):
        response.headers.update(
            {"x-my-custom-uuid": request.get("request_id")}
        )


def test_my_abstract_view():
    app = Sanic()

    MyAbstractView.register(app=app)

    _, response = app.test_client.get("/")

    assert response.status == 200
    assert response.json.get("hello") == "world"
    assert "x-my-custom-uuid" not in response.headers

    _, response = app.test_client.get("/baz")

    assert response.status == 200
    assert response.json.get("hello") == "world"
    assert "x-my-custom-uuid" not in response.headers

    _, response = app.test_client.get("/foo")

    assert response.status == 200
    assert response.json.get("another") == "test"
    assert "x-my-custom-uuid" not in response.headers

    _, response = app.test_client.get("/oof")

    assert response.status == 200
    assert response.json.get("another") == "test"
    assert "x-my-custom-uuid" not in response.headers

    _, response = app.test_client.get("/bar")

    assert response.status == 404
    assert "x-my-custom-uuid" not in response.headers


def test_my_custom_view():
    app = Sanic()
    AnotherCustomView.register(app=app)

    _, response = app.test_client.get("/")

    assert response.status == 404
    assert "x-my-custom-uuid" in response.headers


def test_my_custom_and_abstract_view():
    app = Sanic()
    MyAbstractView.register(app=app)
    AnotherCustomView.register(app=app)

    _, response = app.test_client.get("/")

    assert response.status == 200
    assert response.json.get("hello") == "world"
    assert "x-my-custom-uuid" in response.headers

    _, response = app.test_client.get("/baz")

    assert response.status == 200
    assert response.json.get("hello") == "world"
    assert "x-my-custom-uuid" in response.headers

    _, response = app.test_client.get("/foo")

    assert response.status == 200
    assert response.json.get("another") == "test"
    assert "x-my-custom-uuid" in response.headers

    _, response = app.test_client.get("/oof")

    assert response.status == 200
    assert response.json.get("another") == "test"
    assert "x-my-custom-uuid" in response.headers

    _, response = app.test_client.get("/bar")

    assert response.status == 404
    assert "x-my-custom-uuid" in response.headers
