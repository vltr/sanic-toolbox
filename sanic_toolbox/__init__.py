import logging

from .blueprint import _Blueprint as Blueprint
from .blueprint import _Sanic as Sanic
from .blueprint import bp_middleware
from .lazyapp import lazyapp
from .utils import load_module, search_modules

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = '0.3.0'
__description__ = 'A general utility toolbox for Sanic to make middleware workflows simple and presumable, without monkey patching, for plugins and applications'


__all__ = [
    'lazyapp',
    'Blueprint',
    'Sanic',
    'bp_middleware',
    'search_modules',
    'load_module',
]
