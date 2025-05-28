#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

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