#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

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