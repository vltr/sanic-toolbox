import asyncio
import random

import pytest
from sanic import Sanic
from sanic.response import json

from sanic_toolbox import lazyapp
from sanic_toolbox.exceptions import (BeforeAndAfterNotSupported, TaskNotFound)


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
        assert Result.count == 1

    dumb_app.add_task(some_task_01)

    async def some_task_02():
        add_to_task_result(2)
        assert Result.count == 19

    dumb_app.add_task(some_task_02)

    async def some_task_03():
        add_to_task_result(4)
        assert Result.count == 31

    dumb_app.add_task(some_task_03)

    async def some_task_04():
        add_to_task_result(8)
        assert Result.count == 27

    dumb_app.add_task(some_task_04, before=some_task_03)

    async def some_task_05():
        add_to_task_result(16)
        assert Result.count == 17

    dumb_app.add_task(some_task_05, after=some_task_01)

    with pytest.raises(BeforeAndAfterNotSupported):

        async def somefn_that_would_not_work():
            add_to_task_result(99)
            assert Result.count == random.randint(0, 500)

        dumb_app.add_task(
            somefn_that_would_not_work, after=some_task_01, before=some_task_02
        )

    async def some_task_not_registered():
        await asyncio.sleep(0.0)

    async def some_task_that_wont_work_either():
        add_to_task_result(200)
        assert Result.count == random.randint(0, 500)

    with pytest.raises(TaskNotFound):

        dumb_app.add_task(
            some_task_that_wont_work_either, after=some_task_not_registered
        )

    with pytest.raises(TaskNotFound):

        dumb_app.add_task(
            some_task_that_wont_work_either, before=some_task_not_registered
        )

    async def some_task_06():
        add_to_task_result(32)

    dumb_app.add_task(some_task_06)

    yield dumb_app


def test_tasks(a_lazy_app):
    dumb_app = a_lazy_app

    real_app = dumb_app(Sanic(name='test-tasks'))

    @real_app.route('/')
    async def test(request):
        return json({'hello': 'world'})

    request, response = real_app.test_client.get('/')
    assert response.status == 200
    assert Result.count == 63
