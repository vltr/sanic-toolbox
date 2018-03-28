from collections import defaultdict, deque
from copy import deepcopy
from functools import partial

from .exceptions import (
    BeforeAndAfterNotSupported,
    ListenerNotFound,
    MiddlewareNotFound,
    TaskNotFound,
)


class LazyApplication:
    """Most of the code here was taken directly from Sanic Application class.
    I'm kind of ashame of that, but it'll do for now.
    """

    def __init__(self):
        self._listeners = defaultdict(list)
        self._request_middleware = deque()
        self._response_middleware = deque()
        self._tasks = deque()

    def listener(self, event, *, before=None, after=None):
        """Create a listener from a decorated function.
        :param event: event to listen to
        """

        def decorator(listener):
            if any([before, after]):
                if all([before, after]):
                    raise BeforeAndAfterNotSupported

            if before:
                if before not in self._listeners[event]:
                    raise ListenerNotFound

                idx = self._listeners[event].index(before)
                self._listeners[event].insert(idx, listener)
            elif after:
                if after not in self._listeners[event]:
                    raise ListenerNotFound

                idx = self._listeners[event].index(after)
                self._listeners[event].insert(idx + 1, listener)
            else:
                self._listeners[event].append(listener)
            return listener

        return decorator

    def register_middleware(
        self, middleware, attach_to='request', before=None, after=None
    ):

        attach_middleware_to = []
        if attach_to == 'request':
            attach_middleware_to = self._request_middleware
        if attach_to == 'response':
            attach_middleware_to = self._response_middleware

        if any([before, after]):
            if all([before, after]):
                raise BeforeAndAfterNotSupported

        if before:
            if before not in attach_middleware_to:
                raise MiddlewareNotFound

            idx = attach_middleware_to.index(before)
            attach_middleware_to.insert(idx, middleware)
        elif after:
            if after not in attach_middleware_to:
                raise MiddlewareNotFound

            idx = attach_middleware_to.index(after)
            attach_middleware_to.insert(idx + 1, middleware)
        else:
            attach_middleware_to.append(middleware)
        return middleware

    def middleware(self, middleware_or_request, *, before=None, after=None):
        """Decorate and register middleware to be called before a request.
        Can either be called as @app.middleware or @app.middleware('request')
        """
        # Detect which way this was called, @middleware or @middleware('AT')
        if callable(middleware_or_request):
            return self.register_middleware(
                middleware_or_request, before=before, after=after
            )

        else:
            return partial(
                self.register_middleware,
                attach_to=middleware_or_request,
                before=before,
                after=after,
            )

    def add_task(self, task, *, before=None, after=None):
        """Schedule a task to run later, after the loop has started.
        Different from asyncio.ensure_future in that it does not
        also return a future, and the actual ensure_future call
        is delayed until before server start.
        :param task: future, couroutine or awaitable
        """

        if any([before, after]):
            if all([before, after]):
                raise BeforeAndAfterNotSupported

        if before:
            if before not in self._tasks:
                raise TaskNotFound

            idx = self._tasks.index(before)
            self._tasks.insert(idx, task)
        elif after:
            if after not in self._tasks:
                raise TaskNotFound

            idx = self._tasks.index(after)
            self._tasks.insert(idx + 1, task)
        else:
            self._tasks.append(task)

    def clone(self):
        lazyapp = LazyApplication()
        lazyapp._listeners = deepcopy(self._listeners)
        lazyapp._request_middleware = deepcopy(self._request_middleware)
        lazyapp._response_middleware = deepcopy(self._response_middleware)
        lazyapp._tasks = deepcopy(self._tasks)
        return lazyapp

    def apply(self, app, sanic_response_order, sanic_listener_stop_order):
        for task in self._tasks:
            app.add_task(task())
        for middleware in self._request_middleware:
            app.register_middleware(middleware, 'request')
        if not sanic_response_order:
            self._response_middleware.reverse()
        for middleware in self._response_middleware:
            app.register_middleware(middleware, 'response')
        for event, listeners in self._listeners.items():
            if event in (
                'before_server_stop', 'after_server_stop'
            ) and not sanic_listener_stop_order:
                listeners.reverse()
            for listener in listeners:
                app.listener(event)(listener)

        self.clear()
        return app

    def clear(self):
        # clear everything
        self._tasks.clear()
        self._request_middleware.clear()
        self._response_middleware.clear()
        self._listeners.clear()

    def __call__(
        self, app, sanic_response_order=True, sanic_listener_stop_order=True
    ):
        return self.apply(
            app,
            sanic_response_order=sanic_response_order,
            sanic_listener_stop_order=sanic_listener_stop_order,
        )


def lazyapp():
    return LazyApplication()


__all__ = ('lazyapp')
