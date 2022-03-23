import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--optional",
        action="store_true",
        help="run the tests only in case of that command line (marked with marker @optional)",
    )


def pytest_runtest_setup(item):
    if "optional" in item.keywords and not item.config.getoption("--optional"):
        pytest.skip("need --optional option to run this test")
