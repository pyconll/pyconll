def pytest_addoption(parser):
    parser.addoption(
        '--corpora-versions',
        action='store',
        default='*',
        help='The comma delimited list of corpora versions to run corpora tests on (or wildcard).'
    )

    parser.addoption(
        '--corpora-test-skip-write',
        action='store_true',
        default=False,
        help='Flag if the corpora test should skip the writing component.')
