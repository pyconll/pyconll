from pathlib import Path


def fixture_location(name: str) -> Path:
    """
    Get the file location of the fixture with the given name.
    """
    return Path(__file__).parent / "fixtures" / name


def assert_tree_structure(tree, children_paths):
    """
    Assert a tree structure from tree node paths to values.

    Args:
        tree: The tree whose structure to inspect.
        children_paths: A dictionary from child indices to token indices.
    """
    for path, value in children_paths.items():
        cur = tree
        for component in path:
            cur = cur[component]

        assert cur.data == value
