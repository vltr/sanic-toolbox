import importlib
import inspect
import sys
from pathlib import Path

import pytest

from sanic_toolbox import search_modules, load_module


def test_import():
    with pytest.raises(ValueError):
        for module_name in search_modules('myapp'):
            assert module_name is not None

    root = Path(__file__).absolute().parent / 'resources'
    sys.path.append(str(root))

    assert importlib.import_module('myapp') is not None

    for module_name in search_modules('myapp'):
        assert module_name[-1] in ['thiswillnotimport', 'simplestuff']
        module = load_module(module_name)
        for key in dir(module):
            if key.startswith('_'):
                continue

            if inspect.isfunction(getattr(module, key)):
                assert key == 'hello'
                assert getattr(module, key).__call__() == 'world'

    for module_name in search_modules('myapp', 'tools'):
        assert module_name == ['myapp', 'tools', 'simpleobj']
        module = load_module(module_name)
        for key in dir(module):
            if key.startswith('_'):
                continue

            if inspect.isclass(getattr(module, key)):
                cls_ = getattr(module, key)
                assert cls_.__name__ == 'MyObject'
                instance = cls_()
                assert instance.echo('my oh my') == 'my oh my'

    with pytest.raises(ValueError):
        for module_name in search_modules('myapp', 'tools', 'simpleobj'):
            assert module_name is not None

    sys.path.remove(str(root))
