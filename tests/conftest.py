def pytest_addoption(parser):
    parser.addoption(
        "--corpora-versions",
        action="store",
        default="*",
        help="The comma delimited list of corpora versions to run corpora tests on (or wildcard).",
    )

    parser.addoption(
        "--corpora-skip-write",
        action="store_true",
        default=False,
        help="Flag if the corpora tests should skip the writing component.",
    )

    parser.addoption(
        "--corpora-skip-fixture",
        action="store_true",
        default=False,
        help="Flag if the corpora tests should skip the setup fixtures (if it can be assumed the corpora already exist).",
    )
