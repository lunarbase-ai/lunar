import pytest
from lunarbase.persistence.connections import LocalFilesStorageConnection
from pathlib import Path
import os

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

def test_builds_a_path(connection):
    params = ["path", "to", "file"]
    path = connection.build_path(*params)
    expected = str(Path(*params))
    assert path == expected

def test_find_files(connection, sample_files):
    results = connection.glob(sample_files, pattern="*/*.txt")
    result_names = sorted([p.name for p in results])
    assert result_names == ["file1.txt", "file2.txt", "file3.txt"]

def test_find_no_files(connection, tmp_path):
    results = connection.glob(tmp_path, pattern="*.doesnotexist")
    assert results == []

def test_resolves_relative_path(connection, tmp_path):
    connection._lunar_base_path = str(tmp_path)
    rel_path = "foo/bar.txt"
    resolved = connection._resolve_path(rel_path)
    assert str(resolved) == str(tmp_path / "foo" / "bar.txt")
    assert resolved.is_absolute()

def test_resolves_absolute_path(connection, tmp_path):
    # Patch the connection's _lunar_base_path to tmp_path for isolation
    connection._lunar_base_path = str(tmp_path)
    abs_path = tmp_path / "foo" / "bar.txt"
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    resolved = connection._resolve_path(str(abs_path))
    assert resolved == abs_path.resolve()

def test_resolves_absolute_path_outside_of_base(connection, tmp_path):
    connection._lunar_base_path = str(tmp_path)
    # Use the OS root as a guaranteed outside path
    outside_path = Path(os.path.abspath(os.sep)) / "should_not_exist.txt"
    with pytest.raises(ValueError, match="outside of the base path"):
        connection._resolve_path(str(outside_path))

def test_resolve_path_no_base(connection, tmp_path, monkeypatch):
    # Patch the connection's _lunar_base_path to None to simulate unset base
    connection._lunar_base_path = None
    rel_path = "foo/bar.txt"
    cwd = Path(".").resolve()
    resolved = connection._resolve_path(rel_path)
    assert str(resolved) == str(cwd / "foo" / "bar.txt")
    assert resolved.is_absolute()