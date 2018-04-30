import importlib
import inspect
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def search_modules(root, *args):
    if root not in sys.modules:
        raise ValueError('"{}" is not a valid (or loaded) module'.format(root))

    root_mod = sys.modules[root]
    root_mod_path = Path(root_mod.__file__).parent
    for a in args:
        root_mod_path /= a
    if not root_mod_path.is_dir():
        raise ValueError(
            '"{!s}" is not a valid directory'.format(root_mod_path)
        )

    relative_module_root = [root, *args]
    for module_name in sorted(
        map(
            lambda p: inspect.getmodulename(str(p)), root_mod_path.glob("*.py")
        )
    ):
        if module_name == "__init__":
            continue

        yield [*relative_module_root, module_name]


def load_module(module_name):
    logger.debug('importing "{name}"'.format(name=".".join(module_name)))
    try:
        return importlib.import_module(".".join(module_name))

    except ImportError as ie:
        logger.exception(
            'could not import module "{}": {}'.format(
                ".".join(module_name), ie.msg
            )
        )
        return None


__all__ = ["search_modules", "load_module"]
