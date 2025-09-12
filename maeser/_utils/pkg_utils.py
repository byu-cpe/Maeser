# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Utility to auto-discover and import all submodules/subpackages into a package.

Made with help from ChatGPT. Calling autoimport_all within an __init__.py file will import
all modules and subpackages located in that package's root directory. This should hopefully prevent
accidentally not including new modules in their respective subpackage.
"""

import pkgutil
from importlib import import_module
from types import ModuleType


def autoimport_all(
    pkg: ModuleType, include_packages: bool = False, include_nonpublic: bool = False
) -> list[str]:
    """Discovers and import all modules (and optionally subpackages) in the given package.

    Examples:
        To import all modules but skip all packages, add the following line of code to your
        submodule's __init__.py:

        .. code-block:: python

            __all__ = autoimport_all(sys.modules[__name__]) # include_packages=False by default

        To import all modules *and* subpackages:

        .. code-block:: python

            __all__ = autoimport_all(sys.modules[__name__], include_packages=True)

        To import all modules and define custom imports, simply import them and add them to ``__all__``
        in conjunction with ``autoimport_all()``:

        .. code-block:: python

            # Say you want .foo.do_something and ._bar exported as well:
            from .foo import do_something as do_something
            from . import _bar as bar
            # .foo.do_something and ._bar are now exposed as .do_something and .bar

            __all__ = autoimport_all(sys.modules[__name__])
            __all__ += [
                "do_something",
                "bar",
            ]
            # `from . import *` will now import do_something and bar in addition to
            # all other modules in the package.


    Args:
        pkg (ModuleType): The package module object.
        include_packages (bool, optional): If True, includes subpackages as well as modules. Defaults to False.
        include_nonpublic (bool, optional): If True, includes modules whose names have an "_" prefix (e.g. "_foo").
            Defaults to False.

    Returns:
        list[str]: A list of names of all the imported packages.
    """

    names = [
        name
        for _, name, is_pkg in pkgutil.iter_modules(pkg.__path__)
        if (not is_pkg or include_packages) # Only include subpackages if include_packages == True
        and (include_nonpublic or name.find("_") != 0) # Only include non-public packages if include_nonpublic == True
    ]

    for name in names:
        pkg.__dict__[name] = import_module(f".{name}", package=pkg.__name__)

    return names
