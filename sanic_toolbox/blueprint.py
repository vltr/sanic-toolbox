import inspect
from functools import wraps

from sanic import Blueprint, Sanic
from sanic.blueprints import FutureMiddleware


class _Sanic(Sanic):

    def blueprint(self, blueprint, **options):
        super().blueprint(blueprint, **options)
        if hasattr(blueprint, "nested"):
            for bp in blueprint.nested:
                super().blueprint(bp, **options)


class _Blueprint(Blueprint):

    def __init__(
        self,
        name,
        url_prefix,
        *,
        host=None,
        version=None,
        strict_slashes=False
    ):
        super().__init__(
            name,
            url_prefix=url_prefix,
            host=host,
            version=version,
            strict_slashes=strict_slashes,
        )

        self._blueprints = []

    @property
    def nested(self):
        for bp in self._blueprints:
            yield bp

    def register(self, app, options):
        if "url_prefix" in options:
            options.pop("url_prefix")
        super().register(app, options)

    def bp(self, name, url_prefix):
        new_url_prefix = self.url_prefix + url_prefix
        new_name = ".".join([self.name, name])
        bp = _Blueprint(
            new_name,
            url_prefix=new_url_prefix,
            host=self.host,
            version=self.version,
            strict_slashes=self.strict_slashes,
        )
        self._blueprints.append(bp)
        return bp


def bp_middleware(bp, attach_to="request"):

    def middleware(f):

        @wraps(f)
        async def inner_middleware(request, *args):
            if request.path.startswith(bp.url_prefix):
                if attach_to == "request":
                    response = f(request)
                elif attach_to == "response":
                    response = f(request, *args)
                else:
                    # TODO see what fits best here, an custom exception or
                    # just return None?
                    raise Exception("or return None?")  # noqa

                if inspect.isawaitable(response):
                    response = await response  # noqa
                return response

        future_middleware = FutureMiddleware(inner_middleware, [attach_to], {})
        bp.middlewares.append(future_middleware)
        return future_middleware

    return middleware


__all__ = ["_Blueprint", "_Sanic", "bp_middleware"]
