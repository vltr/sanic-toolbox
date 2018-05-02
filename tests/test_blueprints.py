import pytest

from sanic import Blueprint as SanicBlueprint
from sanic.response import json
from sanic_toolbox import Sanic, Blueprint, bp_middleware


class Result:
    # not a fan of globals
    request_middleware = []
    response_middleware = []

    @classmethod
    def clear(cls):
        cls.request_middleware.clear()
        cls.response_middleware.clear()


@pytest.yield_fixture
def myapp():
    blueprint_one = Blueprint("one", url_prefix="/one")
    nested_blueprint = blueprint_one.bp("test", url_prefix="/test")
    blueprint_two = Blueprint("two", url_prefix="/two")
    blueprint_three = SanicBlueprint("three", url_prefix="/three")

    @bp_middleware(nested_blueprint, "request")
    async def hello_from_nested_blueprint(request):
        Result.request_middleware.append("hello_from_blueprint")

    @bp_middleware(nested_blueprint, "response")
    async def goodbye_from_nested_blueprint(request, response):
        Result.response_middleware.append("goodbye_from_blueprint")

    @bp_middleware(blueprint_two, "request")
    async def hello_from_blueprint_two(request):
        return json({"hello": "halted"})

    @blueprint_one.route("/")
    async def one_root(request):
        return json({"hello": "one root"})

    @nested_blueprint.route("/")
    async def nested_root(request):
        return json({"hello": "nested root"})

    @blueprint_two.route("/")
    async def two_root(request):
        return json({"hello": "two root"})

    @blueprint_three.route("/")
    async def three_root(request):
        return json({"hello": "three root"})

    app = Sanic(name="test-blueprints")
    app.blueprint(blueprint_one, url_prefix="/this/will/be/ignored")
    app.blueprint(blueprint_two)
    app.blueprint(blueprint_three, url_prefix="/notthree")

    @app.middleware("request")
    async def on_request(request):
        Result.request_middleware.append("on_request")

    @app.middleware("response")
    async def on_response(request, response):
        Result.response_middleware.append("on_response")

    @app.route("/")
    async def app_root(request):
        return json({"hello": "app root"})

    yield app


def test_strict_blueprint_middleware(myapp):
    request, response = myapp.test_client.get("/")
    assert response.status == 200
    assert Result.request_middleware == ["on_request"]
    assert Result.response_middleware == ["on_response"]

    Result.clear()

    request, response = myapp.test_client.get("/one/test")
    assert response.status == 200
    assert Result.request_middleware == ["hello_from_blueprint", "on_request"]
    assert (
        Result.response_middleware == ["on_response", "goodbye_from_blueprint"]
    )

    Result.clear()


def test_nested_blueprints(myapp):
    request, response = myapp.test_client.get("/")
    assert response.status == 200
    assert response.json.get("hello") == "app root"

    request, response = myapp.test_client.get("/one")
    assert response.status == 200
    assert response.json.get("hello") == "one root"

    request, response = myapp.test_client.get("/two")
    assert response.status == 200
    assert response.json.get("hello") == "halted"

    request, response = myapp.test_client.get("/notthree")
    assert response.status == 200
    assert response.json.get("hello") == "three root"

    request, response = myapp.test_client.get("/one/test")
    assert response.status == 200
    assert response.json.get("hello") == "nested root"

    Result.clear()
