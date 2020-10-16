import hashlib
import os
from pathlib import Path
import tarfile

import pytest
import requests

import pyconll


def _add_file_to_hash(hash_obj, path, block_size):
    """
    Helper method in calculating a path's hash to add the hash of a file.

    Args:
        hash_obj: The object that is able to hash the file contents.
        path: The location of the file.
        block_size: The size of the blocks to read in.
    """
    with open(str(path), 'rb') as f:
        buffer = f.read(block_size)
        while buffer:
            hash_obj.update(buffer)
            buffer = f.read(block_size)


def hash_path(hash_obj, path, block_size):
    """
    Hash a path with a provided hash object with a digest and update function.

    Args:
        hash_obj: The object that is able to hash the file contents.
        path: The location of the file.
        block_size: The size of the blocks to read in.

    Returns:
        The hash of the file object at the path as a string in hex format.
    """
    if path.is_dir():
        for child in sorted(path.iterdir()):
            hash_path(hash_obj, child, block_size)
    else:
        _add_file_to_hash(hash_obj, path, block_size)
    return hash_obj.hexdigest()


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
    attempt = 0
    dest_loc = str(dest)
    byte_loc = 0

    with open(dest_loc, 'wb') as f:
        while attempt < attempts:
            try:
                with requests.get(
                        url,
                        headers={'Range': 'bytes={}-'.format(byte_loc)},
                        stream=True) as r:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                break
            except EOFError:
                byte_loc = os.stat(dest_loc).st_size

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


def url_zip_fixture(fixture_cache, entry_id, contents_hash, url):
    """
    Creates a cacheable fixture that is a url download that is a zip.

    Args:
        fixture_cache: The cache location for the fixtures.
        entry_id: The unique id of the entry in the cache.
        contents_hash: The hexdigest format hash of the fixture's contents.
        url: The url of the zip download.

    Returns:
        The path of the fixture within the cache as the fixture value.
    """
    fixture_cache.mkdir(exist_ok=True)

    fixture_path = fixture_cache / entry_id
    if not fixture_path.exists() or hash_path(hashlib.sha256(), fixture_path,
                                              8192) != contents_hash:
        if not fixture_path.exists():
            fixture_path.mkdir()
        else:
            delete_dir(fixture_path)
            fixture_path.mkdir()

        tmp = fixture_cache / 'fixture.tgz'
        if tmp.exists():
            tmp.unlink()
        download_file(url, tmp, 1024, 3)

        with tarfile.open(str(tmp)) as tf:
            tf.extractall(str(fixture_path))

        tmp.unlink()

    if hash_path(hashlib.sha256(), fixture_path, 4096) != contents_hash:
        raise RuntimeError("Corpora contents do not match expected contents.")

    return fixture_path


def new_fixture(fixture_cache, entry_id, contents_hash, url):
    """
    Creates a new fixture for the integration test of corpora.

    Assumes that the fixture is a zip file located at a url.

    Args:
        fixture_cache: The path to the location on disk to cache all entries.
        entry_id: The unique id associated with this fixture, used for tracking
            in the cache.
        contents_hash: The hash of the expected fixture contents in hexdigest
            format.
        url: The location of the fixture file to download.

    Returns:
        The path where the fixture is located.
    """
    return pytest.fixture(
        lambda: url_zip_fixture(fixture_cache, entry_id, contents_hash, url))


# This entire pipeline could be greatly improved with the right structure which would allow more
# succinct test cases and expressiveness.
# Basically the use of fixtures means that the test does not know much about how the fixture works,
# but that is counter to the actual structure of the test I am making. So I will have to just
# parameterize the test run, and have the fixture type logic in the test. This will be a more useful
# approach as more conll types and formats become supported.


ud_v2_6_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_6',
    '410224894b968f1dc35110fe9f74264a8a1ffe397bbed8442e64200201a1a550',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v2.6.tgz'
)

ud_v2_5_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_5',
    '83ce32268c2acb0f11d906945fb12597883f293a4885d0316d3aeecece18f262',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz'
)

ud_v2_4_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_4',
    'd873035329b3f0244fa3660977b06fd0853b9bc38a5e5b4379e39f2a8738bb01',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz'
)

ud_v2_3_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_3',
    '57ee83751bb21b1e77a29f3848e06c05e15c357438fed3c5e5dc76f59be1c828',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz'
)

ud_v2_2_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_2',
    'f33c6f95e79f209ccfc2081ff66aa7acc21ac988c7ad1264fdd6da25a487a0cb',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz'
)

ud_v2_1_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_1',
    'c6ff449281540bf36cc74d12aee3f1ed8e704e4ff632b36ef18013078e23b95a',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2515/ud-treebanks-v2.1.tgz'
)

ud_v2_0_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_0',
    '3d4e1795f45803a20794aca11cfb47206d27e1ee001052f416311dcb6be67c17',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1983/ud-treebanks-v2.0.tgz'
)


def test_ud_v2_data(ud_v2_6_corpus_root, ud_v2_5_corpus_root, ud_v2_4_corpus_root, ud_v2_3_corpus_root,
                    ud_v2_2_corpus_root, ud_v2_1_corpus_root, ud_v2_0_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.0 data without error.
    """
    corpora = [
        ud_v2_6_corpus_root,
        ud_v2_5_corpus_root,
        ud_v2_4_corpus_root,
        ud_v2_3_corpus_root,
        ud_v2_2_corpus_root,
        ud_v2_1_corpus_root,
        ud_v2_0_corpus_root,
    ]

    for corpus in corpora:
        _test_corpus(corpus, '**/*.conllu')


def _test_corpus(fixture, glob):
    """
    Tests a corpus using the fixture path and the glob for files to test.

    Args:
        fixture: The path of the fixture or where the corpus is.
        glob: The glob string that defines which files in the corpus to parse.
    """
    globs = fixture.glob(glob)
    paths = map(str, globs)

    _test_treebanks(paths)


def _test_treebanks(treebank_paths):
    """
    Test that the provided treebanks can be parsed and written without error.

    Args:
        treebank_paths: An iterator that yields the desired paths to check.
    """
    TMP_OUTPUT_FILE = '__tmp__ud.conllu'

    for path in treebank_paths:
        treebank = pyconll.iter_from_file(path)

        # For each sentence write back and make sure to include the proper
        # newlines between sentences.
        with open(TMP_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for sentence in treebank:
                f.write(sentence.conll())
                f.write('\n\n')

    # Clean up after the last write.
    os.remove(TMP_OUTPUT_FILE)
