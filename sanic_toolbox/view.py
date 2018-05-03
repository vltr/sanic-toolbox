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
        self.__post_init__()

    def __post_init__(self):  # noqa
        pass

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


def make_lazy_view(context_name=None, base_cls=None):
    if context_name is None:
        context_name = "LazyView"
        lazy_views.update(
            {context_name: MetaView(context_name, (AbstractLazyView,), {})}
        )
    if context_name not in lazy_views:
        if base_cls is None:
            base_cls = (AbstractLazyView,)
        else:
            if isinstance(base_cls, (tuple, list)):
                base_cls = (AbstractLazyView, *base_cls)
            else:
                base_cls = (AbstractLazyView, base_cls)
        lazy_views.update({context_name: MetaView(context_name, base_cls, {})})
    return lazy_views.get(context_name)


__all__ = ["lazy_decorate", "make_lazy_view", "ObjectProxy"]
