"""
Internal module to support dynamic code generation. The term IR is borrowed from compiler theory
here. Although it does not exactly describe what is being done, it is used anyway as a short-hand
to refer to the concept of dynamic code generation done within the python process itself.
"""

import random

_used_name_ids = set[str]()


def unique_name_id(prefix: str) -> str:
    # TODO: Do proper namespace handling, probably encapsulate in a class
    # TODO: Also literally all uses of root_ir are for method definition, so maybe re-do that, along
    # with rooted flag
    """ """
    var_name = ""
    suffix = -1
    while suffix < 0 or (var_name in _used_name_ids):
        suffix = random.randint(0, 4294967296)
        var_name = f"{prefix}_{suffix}"
    _used_name_ids.add(var_name)

    return var_name


def root_ir(code: str) -> str:
    """
    Transform the indentation levels of some Python code to have no indentation.

    This is mostly a helper method to allow for easier inline dynamic code creation without
    requiring these strings to have indentation out of sync with the code it is defined with.

    Args:
        code: The code to transform.

    Returns:
        The rooted code with no base indentation.
    """
    lines = code.split("\n")
    if not lines:
        return code

    for first, line in enumerate(lines):
        if line:
            break
    else:
        return code

    prefix_chars = []
    for ch in lines[first]:
        if ch not in " \t":
            break
        if ch != lines[first][0]:
            raise RuntimeError("Inconsistent whitespace usage in IR being reformatted.")

        prefix_chars.append(ch)
    prefix = "".join(prefix_chars)

    new_lines = [lines[first].removeprefix(prefix)]
    for line in lines[first + 1 :]:
        if not line:
            continue
        if not line.startswith(prefix):
            raise RuntimeError("Expected whitespace prefix not found on one of the IR lines.")

        new_lines.append(line.removeprefix(prefix))

    return "\n".join(new_lines)
