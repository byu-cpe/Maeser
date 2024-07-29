import pkg_resources  # part of setuptools

version = pkg_resources.require("maeser")[0].version
print(version)