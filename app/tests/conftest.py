import pytest


@pytest.fixture(scope="module")
def player_log() -> str:
    return "tests/fixtures/Player.log"
