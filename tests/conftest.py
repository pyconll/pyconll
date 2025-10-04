def pytest_addoption(parser):
    parser.addoption('--corpora-test-do-write', action='store_true', default=False, help='Flag if the corpora test should do the writing component.')