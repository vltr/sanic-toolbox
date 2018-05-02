lazy_decorators = {}
lazy_views = {}


def lazy_decorate(*a):

    def decorator(f):
        decorators = [m for m in a if isinstance(m, MockableAttribute)]
        if f in lazy_decorators:
            lazy_decorators[f] += decorators
        else:
            lazy_decorators[f] = decorators
        return f

    return decorator


class MockableAttribute:

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

    def __getattr__(self, item, *a, **kw):
        return MockableAttribute(item, self)


class MetaView(type):

    def __new__(mcls, names, bases, dct):
        proxies = []
        for k, v in dct.items():
            if isinstance(v, ObjectProxy):
                v.name = k
                proxies.append(k)

        dct["_proxies"] = proxies
        cls = super().__new__(mcls, names, bases, dct)

        if not hasattr(cls, "_registry"):
            cls._registry = set()
        if not cls.__ignore__:
            cls._registry.add(cls)
            cls._registry -= set(bases)
        return cls

    def __iter__(cls):
        return iter(cls._registry)

    def register(cls, **kw):
        for klass in cls:
            klass(**kw)


class AbstractLazyView:
    __ignore__ = False

    def __init__(self, **kwargs):
        self._register_objects(**kwargs)

    def _register_objects(self, **kw):
        for key, value in kw.items():
            if key in self._proxies:
                setattr(self, key, value)

                for fn, mocks in lazy_decorators.items():
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


class LazyView(AbstractLazyView, metaclass=MetaView):
    pass


lazy_views.update({None: LazyView})


def get_lazy_view(scope_name=None):
    if scope_name not in lazy_views:
        lazy_views.update(
            {scope_name: MetaView(scope_name, (AbstractLazyView,), {})}
        )
    return lazy_views.get(scope_name)


__all__ = ["lazy_decorate", "get_lazy_view", "ObjectProxy"]
