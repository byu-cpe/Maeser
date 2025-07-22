# Credit to @solaluset on GitHub for this solution: https://github.com/pypa/readme_renderer/issues/163#issuecomment-1679601106

import re
import pathlib

GITHUB_URL = "https://github.com/byu-cpe/Maeser"
README_PATH = "README.md"

with open(README_PATH) as f:
    long_description = f.read()

# links on PyPI should have absolute URLs
long_description = re.sub(
    r"(\[[^\]]+\]\()((?!https?:)[^\)]+)(\))",
    lambda m: m.group(1) + GITHUB_URL + "/blob/master/" + m.group(2) + m.group(3),
    long_description,
)

pathlib.Path(README_PATH).write_bytes(long_description.encode())