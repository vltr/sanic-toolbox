import logging

from .lazyapp import lazyapp

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = '0.1.0'
__description__ = 'A general utility toolbox for Sanic to make middleware workflows simple and presumable, without monkey patching, for plugins and applications'


__all__ = [
    'lazyapp',
]
