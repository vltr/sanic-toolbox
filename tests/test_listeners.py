import asyncio

import pytest
from sanic import Sanic
from sanic.response import json

from sanic_toolbox import lazyapp
from sanic_toolbox.exceptions import (
    BeforeAndAfterNotSupported, ListenerNotFound
)


@pytest.yield_fixture
def a_lazy_app():
    dumb_app = lazyapp()
    start_notifications = []
    stop_notifications = []

    @dumb_app.listener('before_server_start')
    async def notify_server_starting(app, loop):
        start_notifications.append('before_server_start')

    @dumb_app.listener('before_server_start', before=notify_server_starting)
    async def notify_server_starting_way_before(app, loop):
        start_notifications.append('way_before_server_start')

    @dumb_app.listener(
        'before_server_start', after=notify_server_starting_way_before
    )
    async def notify_server_starting_after_way_before(app, loop):
        start_notifications.append('after_way_before_server_start')

    @dumb_app.listener('after_server_start')
    async def notify_after_started(app, loop):
        start_notifications.append('after_server_start')

    @dumb_app.listener('after_server_start', after=notify_after_started)
    async def notify_way_after_started(app, loop):
        start_notifications.append('way_after_server_start')

    @dumb_app.listener('before_server_stop')
    async def notify_server_stopping(app, loop):
        stop_notifications.append('before_server_stop')

    @dumb_app.listener('before_server_stop', after=notify_server_stopping)
    async def after_notify_server_stopping(app, loop):
        stop_notifications.append('after_notify_server_stopping')

    @dumb_app.listener('after_server_stop')
    async def notify_after_stop(app, loop):
        stop_notifications.append('after_server_stop')

    @dumb_app.listener('after_server_stop', before=notify_after_stop)
    async def before_notify_after_stop(app, loop):
        stop_notifications.append('before_notify_after_stop')

    with pytest.raises(BeforeAndAfterNotSupported):

        @dumb_app.listener(
            'after_server_stop',
            before=notify_after_stop,
            after=before_notify_after_stop,
        )
        async def a_method_that_will_breaks(app, loop):
            stop_notifications.append('this_will_not_be_shown')

    async def not_a_valid_listener(app, loop):
        await asyncio.sleep(0.5)

    with pytest.raises(ListenerNotFound):

        @dumb_app.listener('after_server_stop', after=not_a_valid_listener)
        async def another_method_that_will_breaks(app, loop):
            stop_notifications.append('this_will_not_be_shown_too')

    with pytest.raises(ListenerNotFound):

        @dumb_app.listener('after_server_stop', before=not_a_valid_listener)
        async def another_stop_method_that_will_breaks(app, loop):
            stop_notifications.append('this_will_not_be_shown_too')

    yield dumb_app, start_notifications, stop_notifications


def test_listeners_user_order(a_lazy_app):
    dumb_app, start_notifications, stop_notifications = a_lazy_app

    real_app = dumb_app(
        Sanic(name='test-listeners-1'), sanic_listener_stop_order=False
    )

    @real_app.route('/')
    async def test(request):
        return json({'hello': 'world'})

    request, response = real_app.test_client.get('/')
    assert response.status == 200
    assert start_notifications == [
        'way_before_server_start',
        'after_way_before_server_start',
        'before_server_start',
        'after_server_start',
        'way_after_server_start',
    ]

    assert stop_notifications == [
        'before_server_stop',
        'after_notify_server_stopping',
        'before_notify_after_stop',
        'after_server_stop',
    ]


def test_listeners_sanic_order(a_lazy_app):
    dumb_app, start_notifications, stop_notifications = a_lazy_app

    real_app = dumb_app(Sanic(name='test-listeners-2'))

    @real_app.route('/')
    async def test(request):
        return json({'hello': 'world'})

    request, response = real_app.test_client.get('/')
    assert response.status == 200
    assert start_notifications == [
        'way_before_server_start',
        'after_way_before_server_start',
        'before_server_start',
        'after_server_start',
        'way_after_server_start',
    ]

    assert stop_notifications == [
        'after_notify_server_stopping',
        'before_server_stop',
        'after_server_stop',
        'before_notify_after_stop',
    ]
