"""
A set of utilities for parsing configuration information out of the project.
Currently this is information like version, which is specified once, but used in
many areas like packaging and documentation generation.
"""

from typing import Union
from pathlib import Path
import re

CANONICAL_VERSION_PATTERN: str = r"""
    v?
    ((?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?)     # local version
"""

_canonical_regex = re.compile(
    '__version__\\s*=\\s*[\'"]' + CANONICAL_VERSION_PATTERN + '[\'"]',
    re.VERBOSE | re.IGNORECASE
)

_arbitrary_regex = re.compile(
    '__version__\\s*=\\s*[\'"](.+)[\'"]',
    re.VERBOSE | re.IGNORECASE
)

def package_version(path: Union[str, Path]) -> str:
    """
    Parse the version from specified file, assumed to be a versioner module.

    Args:
        path: The path of the file to parse.

    Returns:
        The parsed version file.

    Raises:
        ValueError: If the file is deemed not clear enough to determine version
            information.
    """
    contents = Path(path).read_text()

    # Note that this regex version check is very simple and is not all encompassing
    # but works fine for the given use case and internal nature of the logic.
    m = _canonical_regex.search(contents) or _arbitrary_regex.search(contents)

    if m:
        ver = m.group(1)
        return ver

    raise ValueError('There is no version string identified in the file contents.')
