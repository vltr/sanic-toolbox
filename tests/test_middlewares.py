import asyncio
import random

import pytest
from sanic import Sanic
from sanic.response import json

from sanic_toolbox import lazyapp
from sanic_toolbox.exceptions import (
    BeforeAndAfterNotSupported,
    MiddlewareNotFound,
)


@pytest.yield_fixture
def a_lazy_app():
    dumb_app = lazyapp()

    @dumb_app.middleware("request")
    async def request_one(request):
        request["fake_session"] = ""

    @dumb_app.middleware("request")
    async def request_two(request):
        request["fake_session"] += "bar"

    @dumb_app.middleware("request", before=request_two)
    async def request_three(request):
        request["fake_session"] += "foo"

    @dumb_app.middleware
    async def request_four(request):
        request["no_order"] = 1

    @dumb_app.middleware("response")
    async def response_one(request, response):
        if "Server" not in response.headers:
            response.headers["Server"] = ""
        response.headers["Server"] += "bar"

    @dumb_app.middleware("response", after=response_one)
    async def response_two(request, response):
        if "Server" not in response.headers:
            response.headers["Server"] = ""
        response.headers["Server"] += "baz"

    @dumb_app.middleware("response", before=response_one)
    async def response_three(request, response):
        if "Server" not in response.headers:
            response.headers["Server"] = ""
        response.headers["Server"] += "foo"

    with pytest.raises(BeforeAndAfterNotSupported):

        @dumb_app.middleware("request", before=request_one, after=request_two)
        async def a_middleware_that_will_breaks(request):
            assert 1 == random.randint(0, 200)

    async def not_a_valid_middleware(request):
        await asyncio.sleep(0.5)

    with pytest.raises(MiddlewareNotFound):

        @dumb_app.middleware("request", before=not_a_valid_middleware)
        async def this_middleware_wont_run_1(request):
            request["SHOULD_NOT_EXIST"] = 1

    with pytest.raises(MiddlewareNotFound):

        @dumb_app.middleware("request", after=not_a_valid_middleware)
        async def this_middleware_wont_run_2(request):
            request["SHOULD_NOT_EXIST"] = 1

    yield dumb_app


def test_middleware_user_order(a_lazy_app):
    dumb_app = a_lazy_app

    real_app = dumb_app(
        Sanic(name="test-middlewares-1"), sanic_response_order=False
    )

    @real_app.route("/")
    async def test(request):
        assert request["fake_session"] == "foobar"
        assert request["no_order"] == 1
        with pytest.raises(KeyError):
            assert request["SHOULD_NOT_EXIST"] == 1
        return json({"hello": "world"})

    request, response = real_app.test_client.get("/")
    assert response.headers["Server"] == "foobarbaz"
    assert response.status == 200


def test_listeners_sanic_order(a_lazy_app):
    dumb_app = a_lazy_app

    real_app = dumb_app(Sanic(name="test-middlewares-2"))

    @real_app.route("/")
    async def test(request):
        assert request["fake_session"] == "foobar"
        assert request["no_order"] == 1
        with pytest.raises(KeyError):
            assert request["SHOULD_NOT_EXIST"] == 1
        return json({"hello": "world"})

    request, response = real_app.test_client.get("/")
    assert response.headers["Server"] == "bazbarfoo"
    assert response.status == 200
