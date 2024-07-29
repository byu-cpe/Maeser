import sys
from packaging import version

pypi_version_path = sys.argv[1]
this_version_path = sys.argv[2]

pypi_version = version.parse(open(pypi_version_path).read())
this_version = version.parse(open(this_version_path).read())

if this_version <= pypi_version:
    raise Exception(
        f"This version ({this_version}) is not greater than the pypi version ({pypi_version})"
    )