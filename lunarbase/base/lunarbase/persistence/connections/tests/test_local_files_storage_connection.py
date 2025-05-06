import pytest
from lunarbase.persistence.connections import LocalFilesStorageConnection
from pathlib import Path

@pytest.fixture
def connection(config):
    return LocalFilesStorageConnection(config=config)


def test_build_path(connection):
    params = ["path", "to", "file"]
    path = connection.build_path(*params)
    expected = str(Path(*params))
    assert path == expected

    

