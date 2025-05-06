import pytest
from lunarbase.persistence.connections import LocalFilesStorageConnection


@pytest.fixture
def connection():
    return LocalFilesStorageConnection()


def test_teste(connection):
    assert connection.teste() == 'teste'

    