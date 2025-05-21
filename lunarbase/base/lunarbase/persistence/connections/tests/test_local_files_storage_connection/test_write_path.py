#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

class TestWritePath:
    def test_creates_and_writes_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        content = b"hello world"

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