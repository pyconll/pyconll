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
from .workflow import conditional as _if, fail, partial, pipe, sequence, value


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


@partial
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
            logging.info('Hash for %s matched expected %s.', p, hash_s)
        else:
            logging.info(
                'The current contents of %s do not hash to the expected %s.',
                p, hash_s)
            logging.info('Instead %s hashed as %s. Recreating fixture', p,
                         hash_s)
        return r
    else:
        logging.info('File, %s, does not exist.', p)
        return False


@partial
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


@partial
def download_file_to_dir(url, direc):
    """
    Download a file (final name matching the URL) to a specified directory.

    Args:
        url: The url of the file to download
        direc: The directory to download the file to.
    """
    tmp = direc / _get_filename_from_url(url)
    if tmp.exists():
        tmp.unlink()
    logging.info('Starting to download %s to %s.', url, tmp)
    download_file(url, tmp, 16384, 15)
    logging.info('Download succeeded to %s.', tmp)

    return tmp


@partial
def extract_tgz(p, tgz):
    """
    Extracts a tarfile to a directory.

    Args:
        p: The path to extract to.
        tgz: The tarfile to extract from.
    """
    logging.info('Extracting tarfile to %s.', p)
    with tarfile.open(str(tgz)) as tf:
        tf.extractall(str(p))


def url_zip(entry_id, fixture_cache, contents_hash, zip_hash, url):
    """
    Creates a cacheable fixture that is a url download that is a zip.

    Args:
        entry_id: The unique id of the entry in the cache.
        fixture_cache: The cache location for the fixtures.
        contents_hash: The hexdigest format hash of the fixture's contents.
        zip_hash: The hexdigest format hash of the zip file's contents.
        url: The url of the zip download.

    Returns:
        The path of the fixture within the cache as the fixture value.
    """
    final_path = fixture_cache / entry_id
    fn = _get_filename_from_url(url)
    zip_path = fixture_cache / fn

    download = \
        sequence(
            clean_subdir(fixture_cache, entry_id),
            pipe(
                download_file_to_dir(url, fixture_cache),
                extract_tgz(final_path)
            ),
            _if(
                validate_hash_sha256(final_path, contents_hash),
                value(final_path),
                fail('Fixture for {} in {} was not able to be properly setup.'.
                    format(url, final_path))))

    w = _if(
            validate_hash_sha256(final_path, contents_hash),
            value(final_path),
            _if(
                validate_hash_sha256(zip_path, zip_hash),
                sequence(
                    extract_tgz(final_path, zip_path),
                    _if(
                        validate_hash_sha256(final_path, contents_hash),
                        value(final_path),
                        sequence(
                            zip_path.unlink,
                            download
                        )
                    )
                ),
                download)) # yapf: disable
    return w


# This is the registration for the different corpora. It includes an id, and a
# method of creation as a key-value pair. This registration structure allows
# for the same corpora to easily be used in different tests which are designed
# to holistically evaluate pyconll across large scenarios, like correctness or
# performance. Given the structure of exceptions and marks, I may still need
# some tweaking of what structure works best, but this is a definite improvement
# and is on a path toward more flexibility and robustness.
corpora = {
    'UD v2.7':
    url_zip(
        'UD v2.7', Path('tests/int/_corpora_cache'),
        '38e7d484b0125aaf7101a8c447fd2cb3833235cf428cf3c5749128ade73ecee2',
        'ee61f186ac5701440f9d2889ca26da35f18d433255b5a188b0df30bc1525502b',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3424/ud-treebanks-v2.7.tgz'
    ),
    'UD v2.6':
    url_zip(
        'UD v2.6', Path('tests/int/_corpora_cache'),
        'a28fdc1bdab09ad597a873da62d99b268bdfef57b64faa25b905136194915ddd',
        'a462a91606c6b2534a767bbe8e3f154b678ef3cc81b64eedfc9efe9d60ceeb9e',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v2.6.tgz'
    ),
    'UD v2.5':
    url_zip(
        'UD v2.5', Path('tests/int/_corpora_cache'),
        'dfa4bdef847ade28fa67b30181d32a95f81e641d6c356b98b02d00c4d19aba6e',
        '5ff973e44345a5f69b94cc1427158e14e851c967d58773cc2ac5a1d3adaca409',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz'
    ),
    'UD v2.4':
    url_zip(
        'UD v2.4', Path('tests/int/_corpora_cache'),
        '000646eb71cec8608bd95730d41e45fac319480c6a78132503e0efe2f0ddd9a9',
        '252a937038d88587842f652669cdf922b07d0f1ed98b926f738def662791eb62',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz'
    ),
    'UD v2.3':
    url_zip(
        'UD v2.3', Path('tests/int/_corpora_cache'),
        '359e1989771268ab475c429a1b9e8c2f6c76649b18dd1ff6568c127fb326dd8f',
        '122e93ad09684b971fd32b4eb4deeebd9740cd96df5542abc79925d74976efff',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz'
    ),
    'UD v2.2':
    url_zip(
        'UD v2.2', Path('tests/int/_corpora_cache'),
        'fa3a09f2c4607e19d7385a5e975316590f902fa0c1f4440c843738fbc95e3e2a',
        'a9580ac2d3a6d70d6a9589d3aeb948fbfba76dca813ef7ca7668eb7be2eb4322',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz'
    ),
    'UD v2.1':
    url_zip(
        'UD v2.1', Path('tests/int/_corpora_cache'),
        '36921a1d8410dc5e22ef9f64d95885dc60c11811a91e173e1fd21706b83fdfee',
        '446cc70f2194d0141fb079fb22c05b310cae9213920e3036b763899f349fee9b',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2515/ud-treebanks-v2.1.tgz'
    ),
    'UD v2.0':
    url_zip(
        'UD v2.0', Path('tests/int/_corpora_cache'),
        '4f08c84bec5bafc87686409800a9fe9b5ac21434f0afd9afe1cc12afe8aa90ab',
        'c6c6428f709102e64f608e9f251be59d35e4add1dd842d8dc5a417d01415eb29',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1983/ud-treebanks-v2.0.tgz'
    )
}

marks = {'UD v2.7': pytest.mark.latest}
exceptions = {
    'UD v2.5': [
        Path(
            # There is one token with less than 10 columns.
            'ud-treebanks-v2.5/UD_Russian-SynTagRus/ru_syntagrus-ud-train.conllu'
        )
    ]
}


@pytest.fixture
def corpus(request):
    """
    A utility fixture to merely execute the actual fixture logic as necessary.

    Args:
        request: The pytest indirect request object, which has a param object
            for the underlying fixture argument.

    Returns:
        The value of the execution of the corpus fixture.
    """
    return request.param()


def pytest_generate_tests(metafunc):
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
    if 'corpus' in metafunc.fixturenames:
        testdata = []
        for item in corpora.items():
            exc = exceptions[item[0]] if item[0] in exceptions else []
            if item[0] in marks:
                p = pytest.param(item[1],
                                 exc,
                                 marks=pytest.mark.latest,
                                 id=item[0])
            else:
                p = pytest.param(item[1], exc, id=item[0])

            testdata.append(p)

        metafunc.parametrize(argnames=('corpus', 'exceptions'),
                             argvalues=testdata,
                             indirect=['corpus'])


def test_corpus(corpus, exceptions):
    """
    Tests a corpus using the fixture path and the glob for files to test.

    Args:
        corpus: The path where the corpus is.
        exceptions: A list of paths relative to fixture that are known failures.
    """
    globs = corpus.glob('**/*.conllu')

    for path in globs:
        is_exp = any(path == corpus / exp for exp in exceptions)

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
