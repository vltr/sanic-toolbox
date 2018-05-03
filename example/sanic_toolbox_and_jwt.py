import uuid

from sanic import Sanic
from sanic.response import json

from sanic_jwt import Initialize
from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy

# With curl, run:
#
# curl http://127.0.0.1:8000/auth -d '{}' -H "Content-Type: application/json"
#
# then
#
# curl -iv http://127.0.0.1:8000/ -H "Authorization: Bearer <token>"

LazyView = make_lazy_view()


class MyCustomView(LazyView):
    app = ObjectProxy()
    sanicjwt = ObjectProxy()

    @lazy_decorate(sanicjwt.protected())
    @lazy_decorate(app.route("/", methods=["GET"]))
    async def company_list(self, request):
        return json({"hello": "world"})

    @lazy_decorate(
        app.route("/foo", methods=["GET"]), sanicjwt.protected(debug=False)
    )
    async def another_test(self, request):
        print(self.sanicjwt.config.debug())
        return json({"another": "test"})

    @lazy_decorate(app.listener("before_server_start"))
    async def simple_assert_check(self, app, loop):
        assert self.app == app


class AnotherCustomView(LazyView):
    app = ObjectProxy()

    @lazy_decorate(app.middleware)
    async def create_request_id(self, request):
        request["request_id"] = uuid.uuid4()

    @lazy_decorate(app.middleware("response"))
    async def attach_request_id(self, request, response):
        response.headers.update(
            {"x-my-custom-uuid": request.get("request_id")}
        )


def main():

    async def authenticate(request, *args, **kwargs):
        return {"user_id": 1}

    app = Sanic()
    sanicjwt = Initialize(app, authenticate=authenticate, debug=True)

    LazyView.register(sanicjwt=sanicjwt, app=app)
    app.run(port=8000)


if __name__ == "__main__":
    main()
