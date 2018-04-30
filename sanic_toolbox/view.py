
func_decorators = {}


def decorate(*a):

    def decorator(f):
        decorators = [m for m in a if isinstance(m, MockCall)]
        if f in func_decorators:
            func_decorators[f] += decorators
        else:
            func_decorators[f] = decorators
        return f

    return decorator


class MockCall:

    def __init__(self, attr, proxy):
        self.attr = attr
        self.proxy = proxy
        self.args = None
        self.kwargs = None

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    @property
    def called(self):
        return self.args is not None and self.kwargs is not None


class ObjectProxy:

    def __init__(self):
        self.name = None

    def __getattr__(self, item):
        return MockCall(item, self)


class MetaView(type):

    def __new__(mcls, names, bases, dct):
        proxies = []
        for k, v in dct.items():
            if isinstance(v, ObjectProxy):
                v.name = k
                proxies.append(k)

        dct["_proxies"] = proxies
        cls = super().__new__(mcls, names, bases, dct)
        return cls

    def __init__(cls, names, bases, dct):
        super().__init__(names, bases, dct)
        if not hasattr(cls, "registry"):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases)

    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])

    def __call__(cls, *args, **kw):
        return super().__call__(*args, **kw)

    def apply(cls, **kw):
        for klass in cls.registry:
            klass(**kw)


class View(metaclass=MetaView):

    def __init__(self, **kwargs):
        self._apply_objects(**kwargs)

    def _apply_objects(self, **kw):
        for key, value in kw.items():
            if key in self._proxies:
                setattr(self, key, value)

                for fn, mocks in func_decorators.items():
                    if (
                        hasattr(self, fn.__name__)
                        and getattr(self.__class__, fn.__name__) == fn
                    ):
                        for m in mocks:
                            if m.proxy.name == key:
                                if m.called:
                                    setattr(
                                        self,
                                        fn.__name__,
                                        getattr(value, m.attr).__call__(
                                            *m.args, **m.kwargs
                                        ).__call__(
                                            getattr(self, fn.__name__)
                                        ),
                                    )
                                else:
                                    setattr(
                                        self,
                                        fn.__name__,
                                        getattr(value, m.attr).__call__(
                                            getattr(self, fn.__name__)
                                        ),
                                    )
