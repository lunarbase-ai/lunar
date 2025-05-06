import pytest
from lunarbase.persistence.connections import LocalFilesStorageConnection
from pathlib import Path

@pytest.fixture
def connection(config):
    connector = LocalFilesStorageConnection(config=config).connect()

    yield connector

    connector.disconnect()

@pytest.fixture
def sample_files(tmp_path):
    # Setup: create a small directory tree with files
    a_dir = tmp_path / "a"
    b_dir = tmp_path / "b"
    a_dir.mkdir()
    b_dir.mkdir()

    file1 = a_dir / "file1.txt"
    file2 = a_dir / "file2.txt"
    file3 = b_dir / "file3.txt"

    file1.write_text("content1")
    file2.write_text("content2")
    file3.write_text("content3")
    yield tmp_path

def test_build_path(connection):
    params = ["path", "to", "file"]
    path = connection.build_path(*params)
    expected = str(Path(*params))
    assert path == expected

    

def test_glob_finds_files(connection, sample_files):
    results = connection.glob(sample_files, pattern="*/*.txt")
    result_names = sorted([p.name for p in results])
    assert result_names == ["file1.txt", "file2.txt", "file3.txt"]

def test_glob_no_match(connection, tmp_path):
    results = connection.glob(tmp_path, pattern="*.doesnotexist")
    assert results == []