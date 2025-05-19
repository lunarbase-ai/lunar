#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from lunarbase.persistence.connections import LocalFilesStorageConnection
from pathlib import Path
import os
import json

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


class TestBuildPath:
    def test_builds_a_path(self,connection):
        params = ["path", "to", "file"]
        path = connection.build_path(*params)
        expected = str(Path(*params))
        assert path == expected


class TestGlob:
    def test_find_files(self,connection, sample_files):
        results = connection.glob(sample_files, pattern="*/*.txt")
        result_names = sorted([p.name for p in results])
        assert result_names == ["file1.txt", "file2.txt", "file3.txt"]

    def test_find_no_files(self,connection, tmp_path):
        results = connection.glob(tmp_path, pattern="*.doesnotexist")
        assert results == []

class TestResolvePath:
    def test_resolves_relative_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        rel_path = "foo/bar.txt"
        resolved = connection._resolve_path(rel_path)
        assert str(resolved) == str(tmp_path / "foo" / "bar.txt")
        assert resolved.is_absolute()

    def test_resolves_absolute_path(self, connection, tmp_path):
        # Patch the connection's _lunar_base_path to tmp_path for isolation
        connection._lunar_base_path = str(tmp_path)
        abs_path = tmp_path / "foo" / "bar.txt"
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        resolved = connection._resolve_path(str(abs_path))
        assert resolved == abs_path.resolve()

    def test_raises_value_error_on_absolute_path_outside_of_base(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        # Use the OS root as a guaranteed outside path
        outside_path = Path(os.path.abspath(os.sep)) / "should_not_exist.txt"
        with pytest.raises(ValueError, match="outside of the base path"):
            connection._resolve_path(str(outside_path))

    def test_resolves_path_no_base(self, connection):
        # Patch the connection's _lunar_base_path to None to simulate unset base
        connection._lunar_base_path = None
        rel_path = "foo/bar.txt"
        cwd = Path(".").resolve()
        resolved = connection._resolve_path(rel_path)
        assert str(resolved) == str(cwd / "foo" / "bar.txt")
        assert resolved.is_absolute()

class TestWritePath:
    def test_creates_and_writes_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        content = b"hello world"
        # Should create parent dirs and write content
        result_path = connection.write_path(str(file_path.relative_to(tmp_path)), content)
        assert Path(result_path).exists()
        assert Path(result_path).read_bytes() == content

    def test_overwrites_existing_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"old content")
        new_content = b"new content"
        result_path = connection.write_path(str(file_path.relative_to(tmp_path)), new_content)
        assert Path(result_path).read_bytes() == new_content

    def test_raises_value_error_if_write_path_is_directory(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        dir_path = tmp_path / "foo" / "bar.txt"
        dir_path.mkdir(parents=True)
        with pytest.raises((ValueError, IsADirectoryError)):
            connection.write_path(str(dir_path.relative_to(tmp_path)), b"should fail")

    def test_file_writes_create_parents(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "a" / "b" / "c" / "file.txt"
        content = b"deep content"
        result_path = connection.write_path(str(file_path.relative_to(tmp_path)), content)
        assert Path(result_path).exists()
        assert Path(result_path).read_bytes() == content

class TestReadPath:
    def test_reads_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"content")

        content = connection.read_path(str(file_path.relative_to(tmp_path)))

        assert content == b"content"

    def test_raises_value_error_if_file_does_not_exist(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        with pytest.raises(ValueError, match=f"Path {file_path} does not exist."):
            connection.read_path(str(file_path.relative_to(tmp_path)))

    def test_raises_value_error_if_not_a_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" 
        file_path.mkdir(parents=True, exist_ok=True)
        with pytest.raises(ValueError, match=f"Path {file_path} is not a file."):
            connection.read_path(str(file_path.relative_to(tmp_path)))

class TestGetAsDictFromJson:
    def test_gets_dict_from_json(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text('{"a": 1, "b": [2, 3]}')

        data = connection.get_as_dict_from_json(str(file_path.relative_to(tmp_path)))
        assert data == {"a": 1, "b": [2, 3]}

    def test_raises_value_error_if_file_is_not_json(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("not a json file")
        relative_path_str = str(file_path.relative_to(tmp_path))
        with pytest.raises(ValueError, match=f"Problem encountered with path {relative_path_str}"):
            connection.get_as_dict_from_json(relative_path_str)

class TestSaveDictAsJson:
    def test_creates_json_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "data.json"
        data = {"a": 1, "b": [2, 3]}
        result_path = connection.save_dict_as_json(str(file_path.relative_to(tmp_path)), data)
        assert Path(result_path).exists()
        # Check file content is valid JSON and matches data
        with open(result_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_overwrites_json_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "data.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text('{"old": "data"}')
        new_data = {"new": "value"}
        result_path = connection.save_dict_as_json(str(file_path.relative_to(tmp_path)), new_data)
        with open(result_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == new_data

    def test_raises_value_error_on_invalid_json_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        # Try to save to a directory path
        dir_path = tmp_path / "foo" / "data.json"
        dir_path.mkdir(parents=True)
        with pytest.raises(ValueError, match="already exists and is not a file"):
            connection.save_dict_as_json(str(dir_path.relative_to(tmp_path)), {"fail": True})

    def test_raises_value_error_on_invalid_json_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        # Try to save outside of base path
        outside_path = Path("/should_not_exist.json")
        with pytest.raises(ValueError, match="Problem encountered with path"):
            connection.save_dict_as_json(str(outside_path), {"fail": True})


class TestDelete:
    def test_deletes_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"content")
        connection.delete(str(file_path.relative_to(tmp_path)))
        assert not file_path.exists()

    def test_deletes_directory(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        dir_path = tmp_path / "foo"
        dir_path.mkdir(parents=True, exist_ok=True)
        dir_path.joinpath("file.txt").write_bytes(b"content")
        connection.delete(str(dir_path.relative_to(tmp_path)))
        assert not dir_path.exists()

    def test_raises_value_error_on_invalid_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        outside_path = Path("/should_not_exist.txt")
        with pytest.raises(ValueError, match="Problem encountered with path"):
            connection.delete(str(outside_path))

class TestGetAllAsDictFromJson:
    def test_gets_all_dicts_from_json(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text('{"a": 1, "b": [2, 3]}')

        file_path2 = tmp_path / "foo" / "bar2.json"
        file_path2.parent.mkdir(parents=True, exist_ok=True)
        file_path2.write_text('{"a": 1, "b": [2, 3]}')

        data = connection.get_all_as_dict_from_json(str(file_path.parent.relative_to(tmp_path) / "*.json"))
        assert data == [{"a": 1, "b": [2, 3]}, {"a": 1, "b": [2, 3]}]


    def test_gets_all_dicts_from_json_with_wildcard(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        sub_dir = data_dir / "sub"
        sub_dir.mkdir()

        file1_content = {"id": 1, "name": "item1"}
        file2_content = {"id": 2, "name": "item2"}
        # This file should also be in data_dir but not match "item*.json"
        other_json_content = {"id": 3, "name": "other_item"}
        # This file is in a subdirectory and should not be matched by "data/item*.json"
        sub_file_content = {"id": 4, "name": "sub_item"}

        (data_dir / "item1.json").write_text(json.dumps(file1_content))
        (data_dir / "item2.json").write_text(json.dumps(file2_content))
        (data_dir / "other_item.json").write_text(json.dumps(other_json_content))
        (data_dir / "item_related.txt").write_text("this is not json")
        (sub_dir / "sub_item.json").write_text(json.dumps(sub_file_content))

        results = connection.get_all_as_dict_from_json("data/item*.json")

        assert len(results) == 2

        assert file1_content in results
        assert file2_content in results

        assert other_json_content not in results
