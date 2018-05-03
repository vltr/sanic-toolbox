from sanic import Sanic
from sanic.response import json

from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy


class MyCustomView(make_lazy_view()):
    app = ObjectProxy()

    @lazy_decorate(app.route("/", methods=["GET"]))
    async def company_list(self, request):
        return json({"hello": "world"})


def test_my_custom_view():
    app = Sanic()

    MyCustomView.register(app=app)

    _, response = app.test_client.get("/")

    assert response.status == 200
    assert response.json.get("hello") == "world"
