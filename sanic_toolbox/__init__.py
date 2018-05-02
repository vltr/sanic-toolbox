import logging

from .blueprint import _Blueprint as Blueprint
from .blueprint import _Sanic as Sanic
from .blueprint import bp_middleware
from .utils import load_module, search_modules
from .view import get_lazy_view, lazy_decorate, ObjectProxy

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "0.4.0"
__description__ = "A general utility toolbox for Sanic without monkey patching, for plugins and applications"


__all__ = [
    "lazyapp",
    "Blueprint",
    "Sanic",
    "bp_middleware",
    "search_modules",
    "load_module",
    "get_lazy_view",
    "ObjectProxy",
    "lazy_decorate",
]
