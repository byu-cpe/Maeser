"""
Utility to auto-discover and import all submodules/subpackages into a package.

Made with help from ChatGPT. Calling autoimport_all within an __init__.py file will import
all modules and subpackages located in that package's root directory. This should hopefully prevent
accidentally not including new modules in their respective subpackage.
"""

import pkgutil
from importlib import import_module
from types import ModuleType

def autoimport_all(pkg: ModuleType, include_packages: bool = False) -> list[str]:
    """Discovers and import all modules (and optionally subpackages) in the given package.

    To use this in a subpackage, add the following line of code to your submodule's __init__.py:

    ```python
    __all__ = autoimport_all(sys.modules[__name__], include_packages=False)
    ```

    Args:
        pkg (ModuleType): The package module object.
        include_packages (bool, optional): If True, includes subpackages as well as modules. Defaults to False.

    Returns:
        list[str]: A list of names of all the imported packages.
    """

    names = [
        name
        for _, name, is_pkg in pkgutil.iter_modules(pkg.__path__)
        if not is_pkg or include_packages
    ]

    for name in names:
        pkg.__dict__[name] = import_module(f".{name}", package=pkg.__name__)

    return names