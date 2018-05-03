# sanic-toolbox

[![Latest PyPI version](https://img.shields.io/pypi/v/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![Python versions](https://img.shields.io/pypi/pyversions/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![Version status](https://img.shields.io/pypi/status/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![MIT License](https://img.shields.io/pypi/l/sanic-toolbox.svg)](https://raw.githubusercontent.com/vltr/sanic-toolbox/master/LICENSE)
[![Build Status](https://travis-ci.org/vltr/sanic-toolbox.svg?branch=master)](https://travis-ci.org/vltr/sanic-toolbox)

Some useful classes to work with Sanic (that might depend on what you want to do with it).
**NOTE**: Those are likely (and mostly) experimentations with Sanic and probably will change over time until it reaches a stable version with all _necessary_<sup>1</sup> tools working (and seamlessly). Please, [open up an issue](https://github.com/vltr/sanic-toolbox/issues) if you need support or anything else related (bugs included, of course!), since it is not ready for production (yet).

<sub><sup>[1]</sup> definition of what this means to be defined yet.</sub>

## Features

- [x] Do not monkey patch things inside Sanic
- [x] Make simple Sanic structures "lazy" and "reusable"
- [x] Ability to work with blueprints, too!
- [x] Support for a wide range of plugins usage


## Getting started

To install:

```
$ pip install sanic-toolbox
```

The main usage of `sanic-toolbox` is based on the possibility to create lazy objects representing callables or direct injection of objects to simplify the development of your Sanic based applications.

### Quick Example

```python
from sanic import Sanic
from sanic.response import json

from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy


class MyCustomView(make_lazy_view()):
    app = ObjectProxy()

    @lazy_decorate(app.route("/", methods=["GET"]))
    async def company_list(self, request):
        return json({"hello": "world"})


def main():
    app = Sanic()
    MyCustomView.register(app=app)
    app.run(port=8000)


if __name__ == "__main__":
    main()
```

Now, testing would be as simple as:

```
$ curl -iv http://127.0.0.1:8000/
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/7.59.0
> Accept: */*
>
< HTTP/1.1 200 OK
HTTP/1.1 200 OK
< Connection: keep-alive
Connection: keep-alive
< Keep-Alive: 5
Keep-Alive: 5
< Content-Length: 17
Content-Length: 17
< Content-Type: application/json
Content-Type: application/json

<
* Connection #0 to host 127.0.0.1 left intact
{"hello":"world"}

```

### Complex Example

What if we wanted to quickly prototype a Sanic extension, like [Sanic Session](https://github.com/subyraman/sanic_session)?

```python
import binascii
import os

from sanic import Sanic
from sanic.response import text

import ujson
from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy

LazyView = make_lazy_view()


class MyInterface:

    def __init__(self):
        self.session_store = dict()

    async def open(self, request) -> dict:
        sid = request.headers.get('sid', None)

        if sid is None:
            sid = binascii.hexlify(os.urandom(32)).decode('utf-8')
            request.headers['sid'] = sid

        if sid not in self.session_store:
            self.session_store[sid] = ujson.dumps({'sid': sid})
        session_dict = ujson.loads(self.session_store[sid])
        request['session'] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        if 'session' not in request:
            return

        sid = request['session']['sid']
        val = ujson.dumps(request['session'])
        self.session_store[sid] = val
        response.headers['sid'] = sid


class SanicSession(LazyView):
    app = ObjectProxy()
    interface = ObjectProxy()

    @lazy_decorate(app.middleware("request"))
    async def add_session_to_request(self, request):
        await self.interface.open(request)

    @lazy_decorate(app.middleware("response"))
    async def save_session(self, request, response):
        await self.interface.save(request, response)


def main():
    app = Sanic(name="my-sanic-session")
    interface = MyInterface()
    SanicSession.register(app=app, interface=interface)

    @app.route('/')
    async def index(request):
        if not request['session'].get('foo'):
            request['session']['foo'] = 0
        request['session']['foo'] += 1
        return text(request['session']['foo'])

    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == '__main__':
    main()
```

Let's test it:

```
$ curl -iv http://127.0.0.1:8000/
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/7.59.0
> Accept: */*
>
< HTTP/1.1 200 OK
HTTP/1.1 200 OK
< Connection: keep-alive
Connection: keep-alive
< Keep-Alive: 5
Keep-Alive: 5
< sid: adb78fc4ee3482f5262c5974402111c838323d80d8a62feb9e62486a71e68dbf
sid: adb78fc4ee3482f5262c5974402111c838323d80d8a62feb9e62486a71e68dbf
< Content-Length: 1
Content-Length: 1
< Content-Type: text/plain; charset=utf-8
Content-Type: text/plain; charset=utf-8

<
* Connection #0 to host 127.0.0.1 left intact
1

$ curl -iv -H "Sid: adb78fc4ee3482f5262c5974402111c838323d80d8a62feb9e62486a71e68dbf" http://127.0.0.1:8000/
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/7.59.0
> Accept: */*
> Sid: adb78fc4ee3482f5262c5974402111c838323d80d8a62feb9e62486a71e68dbf
>
< HTTP/1.1 200 OK
HTTP/1.1 200 OK
< Connection: keep-alive
Connection: keep-alive
< Keep-Alive: 5
Keep-Alive: 5
< sid: adb78fc4ee3482f5262c5974402111c838323d80d8a62feb9e62486a71e68dbf
sid: adb78fc4ee3482f5262c5974402111c838323d80d8a62feb9e62486a71e68dbf
< Content-Length: 1
Content-Length: 1
< Content-Type: text/plain; charset=utf-8
Content-Type: text/plain; charset=utf-8

<
* Connection #0 to host 127.0.0.1 left intact
2
```

Great! It does work! But, remember, **do not use** the above code in production!

You can check this example [here](https://raw.githubusercontent.com/vltr/sanic-toolbox/master/example/sanic_session_alike.py). All credits for [Sanic Session](https://github.com/subyraman/sanic_session) belong to its respective authors.


## Rationale

Great, you want to build a Sanic app! Allright, so, how would you split all functionality and endpoints for a mid-sized application? As for Sanic, it may be quite simple, you can simply create an instance and import everywhere in your code:

```python
# myapp/__init__.py

from Sanic import Sanic

app = Sanic()
```

```python
# myapp/handlers.py

from . import app

@app.route("/")
async def index(request):
    pass
```

Allright, not bad. But if you want some boilerplate, to create your MVC pattern and use some plugins, things can get a little more complicated. You can extend your own `Request`, `Blueprint` or even `Router` classes ... But you still depend on instances.

_Possible solutions_: singletons? Circular references? I don't think so.

Well, you can create classes and pass those instances as arguments to use their decorators ...

```python

def configure(app):

    class MyRoutes:

        @app.route("/")
        async def index(self, request):
            pass

        @app.middleware("request")
        async def my_middleware(self, request):
            pass
```

Hmmmm, not quite ... Or you can do some dirty hacking ...

```python
class MyRoutes:

    async def index(self, request):
        pass

    async def my_middleware(self, request):
        pass

app = Sanic()
routes = MyRoutes()
app.route("/")(routes.index)
app.middleware("request")(routes.my_middleware)
# ...
```

Yeah, well, definitely no.

But, what if you could make all those Sanic and plugin instances _be lazy_, implement all your code (in a manageable way) and still provide the flexibility you are used for using classes? That would be great, right? What if you could reuse code inside your application? Even better, perhaps?

```python
# myapp/some/path/routes.py

from sanic_tolboox import make_lazy_view, lazy_decorator, ObjectProxy

MyAppView = make_lazy_view()

class MyRoutes(MyAppView):  # this changes
    app = ObjectProxy()  # this too

    @lazy_decorate(app.route("/"))  # minor change to the decorator (just wrap)
    async def index(self, request):
        pass

    @lazy_decorate(app.middleware("request"))
    async def my_middleware(self, request):
        pass
```

Not so fantastic. But, you can do this _without_ a Sanic instance is even created. But, how to use it? Its quite simple, actually:

```python
# myapp/server.py

from Sanic import Sanic
from sanic_toolbox import make_lazy_view


def run_sanic():
    app = Sanic()
    # MyAppView.register(app=app)
    # or
    make_lazy_view().register(app=app)  # remember to use the keyword identical to your code
    app.run()
```

## Tracking

**IMPORTANT**: All classes generated (and or subclassed from) sanic-toolbox `make_lazy_view` method are registered for easy development, so the first generated class and all its subclasses needs to fire `register` only once and every class created will be available inside Sanic. More details bellow.


## Function and object references

### **`make_lazy_view([context_name=None[, base_cls=None]])`**

This is the main function that creates (and caches) classes based on [`MetaView`](https://github.com/vltr/sanic-toolbox/blob/master/sanic_toolbox/view.py#L45), the metaclass responsible for mapping class keywords (like `app = ObjectProxy()`) to the actual instances when the method `register` is called (from the resulting class).

The method has two optional parameters: `context_name` and `base_cls`.

- `context_name`, _optional_: is a string that represents the name of this view, more like a context tracking mechanism, so every class or subclass of this "context" will be kept track and automatically assigned when the `register` method of any (of these classes) is called.
- `base_cls`, _optional_: following the pattern of [`declarative_base` from SQLAlchemy](http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/api.html#sqlalchemy.ext.declarative.declarative_base), you can add one or more (using a list or tuple) classes to be inherited into the newest created class. **Note**: Since this method already uses a metaclass, it is not recommended to use other classes that uses metaclasses too!

Example:

```python
import datetime
import uuid

from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy


class DatetimeHelper:

    def add_datetime_to_response(self, response):
        response.headers.update({"x-datetime": datetime.datetime.utcnow().isoformat()})


class IdentificationHelper:

    def add_uuid_to_response(self, response):
        response.headers.update({"x-uid": str(uuid.uuid4())})


BaseView = make_lazy_view("BaseView", (DatetimeHelper, IdentificationHelper))


class MyView(BaseView):

    app = ObjectProxy()

    @lazy_decorate(app.middleware("response"))
    async def my_middleware(self, request, response):
        self.add_datetime_to_response(response)
        self.add_uuid_to_response(response)
```

### **`lazy_decorate(*a)`**

The `lazy_decorate` decorator is a simple utility to wrap all your decorator calls based on instances of the `ObjectProxy`. It maps all calls, arguments, cache them and apply the correct call once the real instance is passed into the `register` function. This decorator receives one or more "proxied calls".

### **`ObjectProxy`**

This is a simple object that tracks all requested attributes to be applied later, similar to a mocking utility.

### **`YourView.register(**kw)`**

When your view is created, you can, after having all instances created, call the `register` method passing only keyword arguments that will be placed on top of `ObjectProxy` instances and instantiate your class. **Note**: remember that the keyword passed into `kw` **must match** the name of the variables created with `ObjectProxy`.

### **`YourView.__post_init__(self)`**

If you need to run some extra boilerplate code after the class is instantiated, the `__post_init__` hook is available to be implemented and will be automatically called _after_ `register` has completed. Of course, you can use `__init__` with `super()`, but this is not encouraged.

Example:

```python
import logging

from sanic.response import json
from sanic_toolbox import make_lazy_view, lazy_decorate, ObjectProxy

BaseView = make_lazy_view("BaseView")
logger = logging.getLogger(__name__)


class MyView(BaseView):

    app = ObjectProxy()

    def __post_init__(self):
        logger.debug("MyView was instantiated!")

    @lazy_decorate(app.route("/"))
    async def index(self, request):
        return json({"hello": "world"})

```

### **`YourView.__ignore__`**

This bool, if set to `True`, will not initialize the class neither keep record of it in the registry. Useful for development.


## Examples

- Quickly prototyping a Session plugin - [example/sanic_session_alike.py](https://github.com/vltr/sanic-toolbox/blob/master/example/sanic_session_alike.py)
- Using [Sanic-JWT](https://github.com/ahopkins/sanic-jwt) with sanic-toolbox - [example/sanic_toolbox_and_jwt.py](https://github.com/vltr/sanic-toolbox/blob/master/example/sanic_toolbox_and_jwt.py)

## To Do

- [ ] Documentation on RTFM (for v1.0)
- [ ] Get rid of the `@lazy_decorate` decorator (it can be merged inside the ObjectProxy)?
- [ ] More examples of how this can be useful
- [ ] Keep dependency usage low (zero for now, this can even have other usages!)

## Thanks

A special thank-you message for [**@ahopkins**](https://github.com/ahopkins) and his precise critic sense, awesome skills and patience! :smile:

Thanks also for the company I work for by letting me work not only in this project but others as well.

## License

MIT, the same as [sanic-jwt](https://raw.githubusercontent.com/ahopkins/sanic-jwt/dev/LICENSE), where the seed of sanic-toolbox came from.
