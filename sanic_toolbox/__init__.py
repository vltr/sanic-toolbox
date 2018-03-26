import logging

from .lazyapp import lazyapp
from .blueprint import _Blueprint as Blueprint
from .blueprint import _Sanic as Sanic

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = '0.2.0'
__description__ = 'A general utility toolbox for Sanic to make middleware workflows simple and presumable, without monkey patching, for plugins and applications'


__all__ = [
    'lazyapp',
    'Blueprint',
    'Sanic'
]
