import pytest
from sanic import Sanic
from sanic.response import json

from sanic_toolbox import lazyapp


class Result:
    # not a fan of globals
    count = 0


@pytest.yield_fixture
def a_lazy_app():
    dumb_app = lazyapp()

    def add_to_task_result(n):
        Result.count += n

    async def some_task_01():
        add_to_task_result(1)

    dumb_app.add_task(some_task_01)

    async def some_task_02():
        add_to_task_result(2)

    dumb_app.add_task(some_task_02)

    async def some_task_03():
        add_to_task_result(4)

    dumb_app.add_task(some_task_03)

    async def some_task_04():
        add_to_task_result(8)

    dumb_app.add_task(some_task_04)

    yield dumb_app


def test_cloning(a_lazy_app):
    dumb_app = a_lazy_app
    cloned_dumb_app = dumb_app.clone()

    real_app = dumb_app(Sanic(name="test-cloning-original"))

    @real_app.route("/")
    async def test(request):
        return json({"hello": "world"})

    request, response = real_app.test_client.get("/")
    assert response.status == 200
    assert Result.count == 15

    clone_app = cloned_dumb_app(Sanic(name="test-cloning-clone"))

    @clone_app.route("/")
    async def test_clone(request):
        return json({"hello": "clone"})

    request, response = clone_app.test_client.get("/")
    assert response.status == 200
    assert Result.count == 30
