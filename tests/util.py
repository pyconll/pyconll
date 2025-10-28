import os


def fixture_location(name):
    """
    Get the file location of the fixture with the given name.
    """
    return os.path.join(os.path.dirname(__file__), "fixtures", name)
