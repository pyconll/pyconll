import hashlib
import logging
import operator
import os
from pathlib import Path
import tarfile
from urllib import parse

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
            tag = child.name.encode(encoding='utf-8', errors='replace')

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
    content_length = int(head_r.headers['Content-Length'])

    attempt = 0
    dest_loc = str(dest)
    byte_loc = 0

    with open(dest_loc, 'wb') as f:
        while attempt < attempts:
            with requests.get(url,
                              headers={'Range': 'bytes={}-'.format(byte_loc)},
                              stream=True) as r:
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


def url_zip_fixture(fixture_cache, entry_id, zip_hash, contents_hash, url):
    """
    Creates a cacheable fixture that is a url download that is a zip.

    Args:
        fixture_cache: The cache location for the fixtures.
        entry_id: The unique id of the entry in the cache.
        zip_hash: The hash of the url zip file, which may still be present and not
            have to be downloaded again.
        contents_hash: The hexdigest format hash of the fixture's contents.
        url: The url of the zip download.

    Returns:
        The path of the fixture within the cache as the fixture value.
    """
    fixture_cache.mkdir(exist_ok=True)

    fixture_path = fixture_cache / entry_id
    if not fixture_path.exists():
        fixture_path.mkdir()

    existing_hash = hash_path(hashlib.sha256(), fixture_path, 8192)
    if existing_hash != contents_hash:
        logging.info(
            'The current contents of %s do not hash to the expected %s.',
            fixture_path, contents_hash)
        logging.info('Instead %s hashed as %s. Recreating fixture',
                     fixture_path, existing_hash)
        delete_dir(fixture_path)
        fixture_path.mkdir()

        need_to_download = True
        tmp = fixture_cache / _get_filename_from_url(url)
        if tmp.exists():
            tmp_hash = hash_path(hashlib.sha256(), fixture_path, 8192)
            if tmp_hash != zip_hash:
                tmp.unlink()
            else:
                need_to_download = False

        if need_to_download:
            logging.info('Starting to download %s to %s', url, tmp)
            download_file(url, tmp, 16384, 15)
            logging.info('Download finished, extracting tarfile to %s.',
                        fixture_path)

        with tarfile.open(str(tmp)) as tf:
            tf.extractall(str(fixture_path))

    cur_hash = hash_path(hashlib.sha256(), fixture_path, 8192)
    if cur_hash != contents_hash:
        raise RuntimeError(
            'Corpora contents do not match expected contents. Expected hash is {} but {} was computed.'
            .format(contents_hash, cur_hash))

    logging.info('Hash for %s matched expected.', fixture_path)

    return fixture_path


def new_fixture(fixture_cache, entry_id, zip_hash, contents_hash, url):
    """
    Creates a new fixture for the integration test of corpora.

    Assumes that the fixture is a zip file located at a url.

    Args:
        fixture_cache: The path to the location on disk to cache all entries.
        entry_id: The unique id associated with this fixture, used for tracking
            in the cache.
        zip_hash: The hash of the url zip file, which may still be present and not
            have to be downloaded again.
        contents_hash: The hash of the expected fixture contents in hexdigest
            format.
        url: The location of the fixture file to download.

    Returns:
        The path where the fixture is located.
    """
    return pytest.fixture(
        lambda: url_zip_fixture(fixture_cache, entry_id, zip_hash, contents_hash, url))


# This entire pipeline could be greatly improved with the right structure which would allow more
# succinct test cases and expressiveness.
# Basically the use of fixtures means that the test does not know much about how the fixture works,
# but that is counter to the actual structure of the test I am making. So I will have to just
# parameterize the test run, and have the fixture type logic in the test. This will be a more useful
# approach as more conll types and formats become supported.

ud_v2_7_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_7',
    'ee61f186ac5701440f9d2889ca26da35f18d433255b5a188b0df30bc1525502b',
    '38e7d484b0125aaf7101a8c447fd2cb3833235cf428cf3c5749128ade73ecee2',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3424/ud-treebanks-v2.7.tgz'
)

ud_v2_6_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_6',
    'a462a91606c6b2534a767bbe8e3f154b678ef3cc81b64eedfc9efe9d60ceeb9e',
    'a28fdc1bdab09ad597a873da62d99b268bdfef57b64faa25b905136194915ddd',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v2.6.tgz'
)

ud_v2_5_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_5',
    '5ff973e44345a5f69b94cc1427158e14e851c967d58773cc2ac5a1d3adaca409',
    'dfa4bdef847ade28fa67b30181d32a95f81e641d6c356b98b02d00c4d19aba6e',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz'
)

ud_v2_4_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_4',
    '252a937038d88587842f652669cdf922b07d0f1ed98b926f738def662791eb62',
    '000646eb71cec8608bd95730d41e45fac319480c6a78132503e0efe2f0ddd9a9',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz'
)

ud_v2_3_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_3',
    '122e93ad09684b971fd32b4eb4deeebd9740cd96df5542abc79925d74976efff',
    '359e1989771268ab475c429a1b9e8c2f6c76649b18dd1ff6568c127fb326dd8f',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz'
)

ud_v2_2_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_2',
    'a9580ac2d3a6d70d6a9589d3aeb948fbfba76dca813ef7ca7668eb7be2eb4322',
    'fa3a09f2c4607e19d7385a5e975316590f902fa0c1f4440c843738fbc95e3e2a',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz'
)

ud_v2_1_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_1',
    '446cc70f2194d0141fb079fb22c05b310cae9213920e3036b763899f349fee9b',
    '36921a1d8410dc5e22ef9f64d95885dc60c11811a91e173e1fd21706b83fdfee',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2515/ud-treebanks-v2.1.tgz'
)

ud_v2_0_corpus_root = new_fixture(
    Path('tests/int/_corpora_cache'), 'ud-v2_0',
    'c6c6428f709102e64f608e9f251be59d35e4add1dd842d8dc5a417d01415eb29',
    '4f08c84bec5bafc87686409800a9fe9b5ac21434f0afd9afe1cc12afe8aa90ab',
    'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1983/ud-treebanks-v2.0.tgz'
)


def test_ud_v2_7_data(ud_v2_7_corpus_root):
    """
    """
    _test_corpus(ud_v2_7_corpus_root, '**/*.conllu')


def test_ud_v2_6_data(ud_v2_6_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.6 data without error.
    """
    _test_corpus(ud_v2_6_corpus_root, '**/*.conllu')


def test_ud_v2_5_data(ud_v2_5_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.5 data without error.
    """
    # TODO: Comment why this is an exception??
    exceptions = [
        Path(
            'ud-treebanks-v2.5/UD_Russian-SynTagRus/ru_syntagrus-ud-train.conllu'
        )
    ]

    _test_corpus(ud_v2_5_corpus_root, '**/*.conllu', exceptions)


def test_ud_v2_4_data(ud_v2_4_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.4 data without error.
    """
    _test_corpus(ud_v2_4_corpus_root, '**/*.conllu')


def test_ud_v2_3_data(ud_v2_3_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.3 data without error.
    """
    _test_corpus(ud_v2_3_corpus_root, '**/*.conllu')


def test_ud_v2_2_data(ud_v2_2_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.2 data without error.
    """
    _test_corpus(ud_v2_2_corpus_root, '**/*.conllu')


def test_ud_v2_1_data(ud_v2_1_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.1 data without error.
    """
    _test_corpus(ud_v2_1_corpus_root, '**/*.conllu')


def test_ud_v2_0_data(ud_v2_0_corpus_root):
    """
    Test that pyconll is able to parse and output all UD 2.0 data without error.
    """
    _test_corpus(ud_v2_0_corpus_root, '**/*.conllu')


def _test_corpus(fixture, glob, exceptions=None):
    """
    Tests a corpus using the fixture path and the glob for files to test.

    Args:
        fixture: The path of the fixture or where the corpus is.
        glob: The glob string that defines which files in the corpus to parse.
        exceptions: A list of paths relative to fixture that are known failures.
    """
    globs = fixture.glob(glob)

    for path in globs:
        is_exp = False \
            if exceptions is None \
            else any(path == fixture / exp for exp in exceptions)

        if is_exp:
            logging.info('Skipping over %s because it is a known failure.',
                         path)
        else:
            _test_treebank(str(path))


def _test_treebank(treebank_path):
    """
    Test that the provided treebank can be parsed and written without error.

    Args:
        treebank_path: The path to the treebank file that is to be parsed and written.
    """
    TMP_OUTPUT_FILE = '__tmp__ud.conllu'

    logging.info('Starting to parse %s', treebank_path)

    treebank = pyconll.iter_from_file(treebank_path)

    # For each sentence write back and make sure to include the proper
    # newlines between sentences.
    with open(TMP_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for sentence in treebank:
            f.write(sentence.conll())
            f.write('\n\n')

    # Clean up afterwards.
    os.remove(TMP_OUTPUT_FILE)
