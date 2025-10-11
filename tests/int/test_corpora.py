from dataclasses import dataclass
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
            logging.info('Instead %s hashed as %s. Recreating fixture', p, s)
        return r
    else:
        logging.info('File, %s, does not exist.', p)
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


def extract_tgz(p: Path, tgz: Path) -> None:
    """
    Extracts a tarfile to a directory.

    Args:
        p: The path to extract to.
        tgz: The tarfile to extract from.
    """
    logging.info('Extracting tarfile to %s.', p)
    with tarfile.open(str(tgz)) as tf:
        tf.extractall(str(p), filter="data")


def url_zip(entry_id: str, contents_hash: str, zip_hash: str,
            url: str) -> Callable[[Path, Path], Path]:
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

    def workflow(zip_path: Path, contents_path: Path) -> Path:
        final_path = contents_path / entry_id

        def download():
            clean_subdir(contents_path, entry_id)
            downloaded_to = download_file_to_dir(url, zip_path)
            extract_tgz(downloaded_to, final_path)

            if validate_hash_sha256(final_path, contents_hash):
                return final_path

            raise RuntimeError(
                f'Fixture for {url} in {final_path} was not able to be properly setup.'
            )

        if validate_hash_sha256(final_path, contents_hash):
            return final_path

        if not validate_hash_sha256(zip_path, zip_hash):
            download()
            return final_path

        extract_tgz(final_path, zip_path)
        if validate_hash_sha256(final_path, contents_hash):
            return final_path

        zip_path.unlink()
        download()
        return final_path

    return workflow


@dataclass
class CorporaRegistration:
    """
    Info to register an online resource as a corpora that can be tested against.
    """

    version: str
    url: str
    zip_hash: str
    contents_hash: str


# This is the registration for the different corpora. It includes an id, and a
# method of creation as a key-value pair. This registration structure allows
# for the same corpora to easily be used in different tests which are designed
# to holistically evaluate pyconll across large scenarios, like correctness or
# performance. Given the structure of exceptions and marks, I may still need
# some tweaking of what structure works best, but this is a definite improvement
# and is on a path toward more flexibility and robustness.
corpora = [
    CorporaRegistration(
        '2.16',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5901/ud-treebanks-v2.16.tgz',
        '87710204b6441736a8a9fed779585aa88b6eeafe231fa2ed9282c0cd9e30960b',
        '6b38dc116ec0da5177b8808e5bead78a4d85cdd47ce007eede99df25b48b27e9'),
    CorporaRegistration(
        '2.15',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5787/ud-treebanks-v2.15.tgz',
        '24ddd9a7e6a291f3882c13febb4d97accfbc6f51633a867963c19e6004d7df97',
        'f84959120d53a701325ba15b3abcb819be8ceda3d1ec6d5edbeda7b5f8b3a358'),
    CorporaRegistration(
        '2.14',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5502/ud-treebanks-v2.14.tgz',
        'a710e09f977fc1ca4aeaf200806a75fbbc46d2c0717c70933a94ad78129ee1af',
        'f6dc84752cce6087b26fd97522dd7171df82492c1004d80e2f6f0224a750c7e5'),
    CorporaRegistration(
        '2.13',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5287/ud-treebanks-v2.13.tgz',
        'd6538ed4c05508be3bb7d9c3448de1062f6f9958c833b93558df300e4b1d3781',
        '57c44ceda3d7b89bc9f84238b73363d09a1d895f34b29e1dad4a5e6e3d1f0cea'),
    CorporaRegistration(
        '2.12',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5150/ud-treebanks-v2.12.tgz',
        '24f876d5ad9dbdc639a33a73f02d12ddfe582e8d4e7f5d08978c8a86680d088c',
        '68152f141a2653a183865cef4ddc64ae146c76fd6effd724c99c2145c80f213c'),
    CorporaRegistration(
        '2.11',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4923/ud-treebanks-v2.11.tgz',
        'd75f7df726761836f797fe6c001c7a1ecce93d93129414ef57cf2262d15707e8',
        '59a87cfbb82524d6dbf4aa27c0c8a8d35fd3e5d3cca3493875a6c4b2c5031a40'),
    CorporaRegistration(
        '2.10',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4758/ud-treebanks-v2.10.tgz',
        'f6deca6ab803abdfa8dca911600f6bc5f214267e348acbd59fd4c4b88db14ea6',
        '572d09f96d52a949750e99caa36519daa3fac366a7643d97e37498873c2ad104'),
    CorporaRegistration(
        '2.9',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4611/ud-treebanks-v2.9.tgz',
        'ca0162be47151a55a5c6c5de24db821c76d67f322fcdfa3fe1436891e9bf2232',
        '7fed278e47358be198303e51f1afca9d77985db550d69c685bbcd5d066d78915'),
    CorporaRegistration(
        '2.8',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3687/ud-treebanks-v2.8.tgz',
        '95d2f4370dc5fe93653eb36e7268f4ec0c1bd012e51e943d55430f1e9d0d7e05',
        'eb5d8941be917d2cb46677cb575f18dd6218bddec446b428a5b96d96ab44c0cd'),
    CorporaRegistration(
        '2.7',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3424/ud-treebanks-v2.7.tgz',
        'ee61f186ac5701440f9d2889ca26da35f18d433255b5a188b0df30bc1525502b',
        '38e7d484b0125aaf7101a8c447fd2cb3833235cf428cf3c5749128ade73ecee2'),
    CorporaRegistration(
        '2.6',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3226/ud-treebanks-v2.6.tgz',
        'a462a91606c6b2534a767bbe8e3f154b678ef3cc81b64eedfc9efe9d60ceeb9e',
        'a28fdc1bdab09ad597a873da62d99b268bdfef57b64faa25b905136194915ddd'),
    CorporaRegistration(
        '2.5',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3105/ud-treebanks-v2.5.tgz',
        '5ff973e44345a5f69b94cc1427158e14e851c967d58773cc2ac5a1d3adaca409',
        '4761846e8c5f7ec7e40a6591f7ef5307ca9e7264da894d05d135514a4ea22a10'),
    CorporaRegistration(
        '2.4',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988/ud-treebanks-v2.4.tgz',
        '252a937038d88587842f652669cdf922b07d0f1ed98b926f738def662791eb62',
        '000646eb71cec8608bd95730d41e45fac319480c6a78132503e0efe2f0ddd9a9'),
    CorporaRegistration(
        '2.3',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2895/ud-treebanks-v2.3.tgz',
        '122e93ad09684b971fd32b4eb4deeebd9740cd96df5542abc79925d74976efff',
        '359e1989771268ab475c429a1b9e8c2f6c76649b18dd1ff6568c127fb326dd8f'),
    CorporaRegistration(
        '2.2',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz',
        'a9580ac2d3a6d70d6a9589d3aeb948fbfba76dca813ef7ca7668eb7be2eb4322',
        'fa3a09f2c4607e19d7385a5e975316590f902fa0c1f4440c843738fbc95e3e2a'),
    CorporaRegistration(
        '2.1',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2515/ud-treebanks-v2.1.tgz',
        '446cc70f2194d0141fb079fb22c05b310cae9213920e3036b763899f349fee9b',
        '36921a1d8410dc5e22ef9f64d95885dc60c11811a91e173e1fd21706b83fdfee'),
    CorporaRegistration(
        '2.0',
        'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1983/ud-treebanks-v2.0.tgz',
        'c6c6428f709102e64f608e9f251be59d35e4add1dd842d8dc5a417d01415eb29',
        '4f08c84bec5bafc87686409800a9fe9b5ac21434f0afd9afe1cc12afe8aa90ab')
]

exceptions = {
    '2.5': [
        Path(
            # There is one token with less than 10 columns.
            'ud-treebanks-v2.5/UD_Russian-SynTagRus/ru_syntagrus-ud-train.conllu'
        )
    ]
}
CORPORA_CACHE = Path('tests/int/_corpora_cache')


@pytest.fixture(scope="module", autouse=True)
def create_corpora_cache() -> None:
    req_dirs = [
        CORPORA_CACHE, CORPORA_CACHE / 'artifacts', CORPORA_CACHE / 'corpora'
    ]
    for d in req_dirs:
        d.mkdir(exist_ok=True)


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
    registration: CorporaRegistration = request.param
    workflow = url_zip(registration.version, registration.contents_hash,
                       registration.zip_hash, registration.url)
    corpus_path = workflow(CORPORA_CACHE / 'artifacts',
                           CORPORA_CACHE / 'corpora')
    return corpus_path


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
    versions_str_filter = metafunc.config.getoption(
        '--corpora-versions').strip()
    versions_set: Optional[set[str]] = None
    if versions_str_filter != '*' or not versions_str_filter:
        versions_set = set(
            filter(lambda v: bool(v), versions_str_filter.split(',')))

    if 'corpus' in metafunc.fixturenames:
        testdata = []
        for registration in corpora:
            if versions_set is None or registration.version in versions_set:
                exc = exceptions.get(registration.version, [])
                p = pytest.param(registration, exc, id=registration.version)
                testdata.append(p)

        metafunc.parametrize(argnames=('corpus', 'exceptions'),
                             argvalues=testdata,
                             indirect=['corpus'])


def test_corpus(corpus: Path, exceptions: list[Path], pytestconfig: pytest):
    """
    Tests a corpus using the fixture path and the glob for files to test.

    Args:
        corpus: The path where the corpus is.
        exceptions: A list of paths relative to fixture that are known failures.
    """
    skip_write: bool = pytestconfig.getoption("--corpora-test-skip-write")

    globs = corpus.glob('**/*.conllu')

    for path in globs:
        is_exp = any(path == corpus / exp for exp in exceptions)

        if is_exp:
            logging.info('Skipping over %s because it is a known exception.',
                         path)
        else:
            _test_treebank(path, skip_write)


def _test_treebank(treebank_path: Path, skip_write: bool) -> None:
    """
    Test that the provided treebank can be parsed and written without error.

    Args:
        treebank_path: The path to the treebank file that is to be parsed and written.
        skip_write: Flag if the writing/serializing of the treebank should also be tested.
    """

    logging.info('Starting to parse %s', treebank_path)

    treebank = pyconll.iter_from_file(treebank_path)

    if not skip_write:
        with tempfile.TemporaryFile(mode='w',
                                    encoding='utf-8') as tmp_output_file:
            for sentence in treebank:
                tmp_output_file.write(sentence.conll())
                tmp_output_file.write('\n\n')
