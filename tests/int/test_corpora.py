import hashlib
import logging
import operator
import os
from pathlib import Path
import tarfile
import tempfile
from typing import Callable, Optional
from urllib import parse

import pytest
import requests

from pyconll.conllu import conllu
from pyconll.format import Format
from pyconll.schema import AbstractSentence
from tests.int.corpora import corpora, CorporaRegistration


def _cross_platform_stable_fs_iter(dir):
    """
    Provides a stable ordering across platforms over a directory Path.

    This allows iteration across filesystems in a consistent way such that case
    sensitivity of the underlying system does not affect how the files are
    iterated.

    Args:
        dir: The Path object that points to the directory to iterate over.

    Returns:
        An iterator that goes over the paths in the directory, defined in such a
        way that is consistent across platforms.
    """
    # As this should work across platforms, paths cannot be compared as is, and
    # the paths must be compared with another in string format. Paths are
    # ordered by case insensitivity, and then ordered by case within any paths
    # that are only different by case. There is a double sort because, a simple
    # case insensitive sort will provide inconsistent results on linux since
    # iterdir does not provide consistently ordered results.
    tupled = map(lambda p: (str(p), p), dir.iterdir())
    by_case = sorted(tupled, key=operator.itemgetter(0))
    by_case_insensitive = sorted(by_case, key=lambda el: el[0].lower())

    only_paths = map(operator.itemgetter(1), by_case_insensitive)

    return only_paths


def _add_file_to_hash(hash_obj, path, block_size):
    """
    Helper method in calculating a path's hash to add the hash of a file.

    Args:
        hash_obj: The object that is able to hash the file contents.
        path: The location of the file.
        block_size: The size of the blocks to read in.
    """
    with open(str(path), "rb") as f:
        buffer = f.read(block_size)
        while buffer:
            hash_obj.update(buffer)
            buffer = f.read(block_size)


def _hash_path_helper(hash_obj, path, block_size):
    """
    Helper to wrap the functionality of updating the actual hash object.

    Args:
        hash_obj: The object that is able to hash the file contents.
        path: The location of the file.
        block_size: The size of the blocks to read in, in bytes.
    """
    if path.is_dir():
        fs_iter = _cross_platform_stable_fs_iter(path)

        for child in fs_iter:
            tag = child.name.encode(encoding="utf-8", errors="replace")

            hash_obj.update(tag)
            _hash_path_helper(hash_obj, child, block_size)
            hash_obj.update(tag)
    else:
        _add_file_to_hash(hash_obj, path, block_size)


def hash_path(hash_obj, path, block_size):
    """
    Hash a path with a provided hash object with a digest and update function.

    Args:
        hash_obj: The object that is able to hash the file contents.
        path: The location of the file.
        block_size: The size of the blocks to read in, in bytes.

    Returns:
        The hash of the file object at the path as a string in hex format.
    """
    _hash_path_helper(hash_obj, path, block_size)
    return hash_obj.hexdigest()


def _get_filename_from_url(url):
    """
    For a url that represents a network file, return the filename part.

    Args:
        url: The url to extract the filename from.

    Returns:
        The filename part at the end of the url with the extension.
    """
    parsed = parse.urlparse(url)
    name = Path(parsed.path).name
    unquoted = parse.unquote(name)

    return unquoted


def download_file(url, dest, chunk_size, attempts):
    """
    Downloads a file from a url, resilient to failures and controlling speed.

    Args:
        url: The url to download the file from.
        dest: The location on disk to store the downloaded file to.
        chunk_size: The size of the file chunks when streaming the download.
        attempts: The number of failures to be resistant to. Assumes the server
            can accept ranged requests on download.
    """
    head_r = requests.head(url)
    content_length = int(head_r.headers["Content-Length"])

    attempt = 0
    dest_loc = str(dest)
    byte_loc = 0

    with open(dest_loc, "wb") as f:
        while attempt < attempts:
            with requests.get(
                url, headers={"Range": "bytes={}-".format(byte_loc)}, stream=True
            ) as r:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    f.flush()

            byte_loc = os.stat(dest_loc).st_size
            if byte_loc >= content_length:
                break

            attempt += 1


def delete_dir(path):
    """
    Recursively deletes a directory and all contents within it.

    Args:
        path: The path to the directory to delete. Must point to a directory.
    """
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir:
            delete_dir(child)

    path.rmdir()


def validate_hash_sha256(p, hash_s):
    """
    Check that a path's SHA256 hash matches the provided string.

    Args:
        p: The path to hash.
        hash_s: The expected hash of the path as a string.
    """
    if p.exists():
        s = hash_path(hashlib.sha256(), p, 8192)
        r = s == hash_s
        if r:
            logging.info("Hash for %s matched expected %s.", p, hash_s)
        else:
            logging.info("The current contents of %s do not hash to the expected %s.", p, hash_s)
            logging.info("Instead %s hashed as %s. Recreating fixture", p, s)
        return r
    else:
        logging.info("File, %s, does not exist.", p)
        return False


def clean_subdir(direc, subdir):
    """
    Create a clean subdirectory in the provided path.

    If the path already exists it is deleted, and then recreated.

    Args:
        direc: The parent directory.
        subdir: The path within the parent to be clean.
    """
    direc.mkdir(exist_ok=True)

    p = direc / subdir
    if not p.exists():
        p.mkdir()
    else:
        delete_dir(p)
        p.mkdir()


def download_file_to_location(url, location, hash_sha256):
    """
    Download a file (final name matching the URL) to a specified directory.

    Args:
        url: The url of the file to download
        location: The location or final destination name of the file.
        hash_sha256: The hash of the file at the end to confirm successful download.
    """
    if location.exists():
        location.unlink()
    logging.info("Starting to download %s to %s.", url, location)
    download_file(url, location, 16384, 15)
    logging.info("Download succeeded to %s.", location)

    if not validate_hash_sha256(location, hash_sha256):
        raise RuntimeError(f"Not able to successfully download url {url} to location {location}.")


def extract_tgz(p: Path, tgz: Path) -> None:
    """
    Extracts a tarfile to a directory.

    Args:
        p: The path to extract to.
        tgz: The tarfile to extract from.
    """
    logging.info("Extracting tarfile to %s.", p)
    with tarfile.open(str(tgz)) as tf:
        tf.extractall(str(p), filter="data")


def url_zip(
    entry_id: str, contents_hash: str, zip_hash: str, url: str
) -> Callable[[bool, Path, Path], Path]:
    """
    Creates a cacheable fixture that is a url download that is a zip.

    Args:
        entry_id: The unique id of the entry in the cache.
        contents_hash: The hexdigest format hash of the fixture's contents.
        zip_hash: The hexdigest format hash of the zip file's contents.
        url: The url of the zip download.

    Returns:
        The path of the fixture within the cache as the fixture value.
    """

    def workflow(skip: bool, artifacts_path: Path, contents_path: Path) -> Path:
        final_path = contents_path / entry_id

        if skip:
            return final_path

        fn = _get_filename_from_url(url)
        zip_path = artifacts_path / fn

        if not validate_hash_sha256(final_path, contents_hash):
            clean_subdir(contents_path, entry_id)
            if not validate_hash_sha256(zip_path, zip_hash):
                download_file_to_location(url, zip_path, zip_hash)

            # Just assume that extraction is successful and has the expected values if
            # the zip is as expected to remove one hashing round.
            extract_tgz(final_path, zip_path)

        return final_path

    return workflow


exceptions = {
    "2.5": [
        Path(
            # There is one token with less than 10 columns.
            "ud-treebanks-v2.5/UD_Russian-SynTagRus/ru_syntagrus-ud-train.conllu"
        )
    ]
}
CORPORA_CACHE = Path("tests/int/_corpora_cache")


@pytest.fixture(scope="module", autouse=True)
def create_corpora_cache() -> None:
    req_dirs = [CORPORA_CACHE, CORPORA_CACHE / "artifacts", CORPORA_CACHE / "corpora"]
    for d in req_dirs:
        d.mkdir(exist_ok=True)


@pytest.fixture
def corpus(request: pytest.FixtureRequest) -> Path:
    """
    A utility fixture to merely execute the actual fixture logic as necessary.

    Args:
        request: The pytest indirect request object, which has a param object
            for the underlying fixture argument.

    Returns:
        The value of the execution of the corpus fixture.
    """
    skip: bool = request.config.getoption("--corpora-skip-fixture")

    registration: CorporaRegistration = request.param
    workflow = url_zip(
        registration.version, registration.contents_hash, registration.zip_hash, registration.url
    )

    corpus_path = workflow(skip, CORPORA_CACHE / "artifacts", CORPORA_CACHE / "corpora")
    return corpus_path


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """
    A pytest utility function for generating tests automatically.

    The current policy is for tests that depend on the corpus fixture, they
    are automatically given tests for all corpora. So any performance,
    correctness, or other tests which are valid across corpora, should include
    the 'corpus' fixture. This corpus fixture will be parameterized by the
    different registered corpora and the data location passed on to the test.

    Args:
        metafunc: The object to parameterize the tests with.
    """
    versions_str_filter = metafunc.config.getoption("--corpora-versions").strip()
    versions_set: Optional[set[str]] = None
    if versions_str_filter != "*" or not versions_str_filter:
        versions_set = set(filter(lambda v: bool(v), versions_str_filter.split(",")))

    if "corpus" in metafunc.fixturenames:
        testdata = []
        for registration in corpora:
            if versions_set is None or registration.version in versions_set:
                exc = exceptions.get(registration.version, [])
                p = pytest.param(registration, exc, id=registration.version)
                testdata.append(p)

        metafunc.parametrize(
            argnames=("corpus", "exceptions"), argvalues=testdata, indirect=["corpus"]
        )


def test_corpus(corpus: Path, exceptions: list[Path], pytestconfig: pytest.Config) -> None:
    """
    Tests a corpus using the fixture path and the glob for files to test.

    Args:
        corpus: The path where the corpus is.
        exceptions: A list of paths relative to fixture that are known failures.
    """
    skip_write: bool = pytestconfig.getoption("--corpora-skip-write")

    globs = corpus.glob("**/*.conllu")

    for path in globs:
        is_exp = any(path == corpus / exp for exp in exceptions)

        if is_exp:
            logging.info("Skipping over %s because it is a known exception.", path)
        else:
            _test_treebank(conllu, path, skip_write)


def _test_treebank[T, S: AbstractSentence](
    format: Format[T, S], treebank_path: Path, skip_write: bool
) -> None:
    """
    Test that the provided treebank can be parsed and written without error.

    Args:
        format: The format that the treebank is in.
        treebank_path: The path to the treebank file that is to be parsed and written.
        skip_write: Flag if the writing/serializing of the treebank should also be tested.
    """

    logging.info("Starting to parse %s", treebank_path)

    treebank = format.iter_from_file(treebank_path)

    count = 0
    with tempfile.TemporaryFile(mode="w", encoding="utf-8") as tmp_output_file:
        for sentence in treebank:
            count += len(sentence.tokens)
            if not skip_write:
                format.write_sentence(sentence, tmp_output_file)
                tmp_output_file.write("\n")
        tmp_output_file.write(str(count))
