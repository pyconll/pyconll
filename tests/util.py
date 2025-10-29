from pathlib import Path


def fixture_location(name: str) -> Path:
    """
    Get the file location of the fixture with the given name.
    """
    return Path(__file__).parent / "fixtures" / name
