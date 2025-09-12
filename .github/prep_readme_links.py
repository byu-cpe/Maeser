# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module prepares the project's readme for publishing to PyPI by replacing all relative repository links to absolute GitHub links.
The script can be run from the command line or imported into another script.

Credit to @solaluset on GitHub for this solution: https://github.com/pypa/readme_renderer/issues/163#issuecomment-1679601106
"""

import sys
import re
import pathlib
from dataclasses import dataclass

GITHUB_URL = "https://github.com/byu-cpe/Maeser"
README_PATH = "README.md"

@dataclass
class _PrintVerbose:
    """
    Simple helper class used for printing when verbose is set to true.
    """
    verbose: bool
    def print(self, *args, **kwargs):
        if verbose:
            print(*args, **kwargs)

def prep_readme_links(verbose: bool = False):
    """Prepares a readme for PyPI by replacing all relative links with absolute links.

    Args:
        verbose (bool, optional): Whether verbose printing should be enabled. Defaults to False.
    """
    # Verbose printing handler
    v = _PrintVerbose(verbose)

    # Get readme text
    v.print(f"Loading readme at {README_PATH}...")
    with open(README_PATH) as f:
        long_description = f.read()

    # links on PyPI should have absolute URLs
    v.print("Replacing relative links with absolute links...")
    long_description = re.sub(
        r"(\[[^\]]+\]\()((?!https?:)[^\)]+)(\))",
        lambda m: m.group(1) + GITHUB_URL + "/blob/master/" + m.group(2) + m.group(3),
        long_description,
    )

    # Result
    v.print("\n".join([
        "::group::Printing Result...",
        f"===== {README_PATH} (pending changes) =====",
        long_description,
        "====================",
        "::endgroup::",
    ]))

    # Write modified readme
    v.print(f"Updating readme at {README_PATH}...")
    pathlib.Path(README_PATH).write_bytes(long_description.encode())
    v.print("Done!")

if __name__ == "__main__":
    verbose: bool = len(sys.argv) > 1 and sys.argv[1] == "-v"
    prep_readme_links(verbose=False)
