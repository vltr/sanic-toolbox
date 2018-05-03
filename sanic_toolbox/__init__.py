import logging

from .view import make_lazy_view, lazy_decorate, ObjectProxy

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "0.5.0"
__description__ = "A general utility toolbox for Sanic without monkey patching, for plugins and applications"


__all__ = ["make_lazy_view", "ObjectProxy", "lazy_decorate"]
