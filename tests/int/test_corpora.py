import hashlib
import logging
import operator
import os
from pathlib import Path
import tarfile

import pytest
import requests

import pyconll

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
    with open(str(path), 'rb') as f:
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
            tag = bytes(child)

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
            logging.info('Attempt %d at downloading %s', attempt + 1, url)

            try:
                with requests.get(
                        url,
                        headers={'Range': 'bytes={}-'.format(byte_loc)},
                        stream=True) as r:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                break
            except EOFError as e:
                byte_loc = os.stat(dest_loc).st_size
                logging.warning('Received error while downloading %s.', url)
                logging.warning('Exception information: %s', e.msg)

                if attempt == attempts - 1:
                    raise

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
            logging.info("The current contents of %s do not hash to the expected %s.", fixture_path, contents_hash)
            delete_dir(fixture_path)
            fixture_path.mkdir()

        tmp = fixture_cache / 'fixture.tgz'
        if tmp.exists():
            tmp.unlink()
        logging.info("Starting to download %s to %s", url, tmp)
        download_file(url, tmp, 1024, 3)

        logging.info("Download succeeded, extracting tarfile to %s.", fixture_path)
        with tarfile.open(str(tmp)) as tf:
            tf.extractall(str(fixture_path))

        tmp.unlink()

    cur_hash = hash_path(hashlib.sha256(), fixture_path, 8192)
    if cur_hash != contents_hash:
        raise RuntimeError("Corpora contents do not match expected contents. Expected hash is {} but {} was computed.".format(content_hash, cur_hash))

    logging.info("Hash for %s matched expected.", fixture_path)

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
    'bcd23b7d7d7a057a89e133a2b7d71bb823d3fcb905ba582f8098adfa3310512c',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v2.6.tgz'
)

ud_v2_5_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_5',
    '8e6fba6c89aee0a8c4f3d0d8e8133ec22e943417e52951bb716243ee561ca54b',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz'
)

ud_v2_4_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_4',
    '1e670fa791fd216f87a9a50fdffabf460951ea7cbba594b7284c3f530cdf878a',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz'
)

ud_v2_3_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_3',
    '570fc9fb6b2c493b02753c3ce6a04fa8b52bcabeb15a2a31e454c93b2052ee3a',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz'
)

ud_v2_2_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_2',
    'eeb822ac97d18b5f72370722b01b64ce5ba9ae249e80d0aa68c06a4ddce31ad2',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz'
)

ud_v2_1_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_1',
    '6ebab4b584547a962551854f9b2083d16ec0edbf59bc1873030dab20f1c8eb96',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2515/ud-treebanks-v2.1.tgz'
)

ud_v2_0_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_0',
    '09fab4954d0ad5564e2ada8fd6f7117ed926732816f7f39d16c7211e32a3fabe',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1983/ud-treebanks-v2.0.tgz'
)


def test_ud_v2_data(ud_v2_6_corpus_root, ud_v2_5_corpus_root,
                    ud_v2_4_corpus_root, ud_v2_3_corpus_root,
                    ud_v2_2_corpus_root, ud_v2_1_corpus_root,
                    ud_v2_0_corpus_root):
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
        ud_v2_0_corpus_root
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
        logging.info('Starting to parse %s', path)
        treebank = pyconll.iter_from_file(path)

        # For each sentence write back and make sure to include the proper
        # newlines between sentences.
        with open(TMP_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for sentence in treebank:
                f.write(sentence.conll())
                f.write('\n\n')

    # Clean up after the last write.
    os.remove(TMP_OUTPUT_FILE)
