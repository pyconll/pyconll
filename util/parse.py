"""
A set of utilities for parsing configuration information out of the project.
Currently this is information like version, which is specified once, but used in
many areas like packaging and documentation generation.
"""

from pathlib import Path
import re


def package_version(path: str | Path) -> str:
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
    contents = Path(path).read_text(encoding='utf-8')

    # Note that this regex version check is very simple and is not all encompassing
    # but works fine for the given use case and internal nature of the logic.
    m = re.search('__version__\\s*=\\s*[\'"]((\\d+\\.)+(\\d+))[\'"]', contents)

    if not m:
        raise ValueError(
            'There is no version string identified in the file contents.')

    ver = m.group(1)
    return ver
