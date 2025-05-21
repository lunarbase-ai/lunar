#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

class TestExists:
    def test_returns_true_for_existing_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"content")
        
        assert connection.exists(str(file_path.relative_to(tmp_path)))

    def test_returns_true_for_existing_directory(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        dir_path = tmp_path / "foo" / "bar"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        assert connection.exists(str(dir_path.relative_to(tmp_path)))

    def test_returns_false_for_nonexistent_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        nonexistent_path = tmp_path / "nonexistent" / "file.txt"
        
        assert not connection.exists(str(nonexistent_path.relative_to(tmp_path)))

    def test_returns_false_for_path_outside_base(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        outside_path = Path("/should_not_exist.txt")
        
        assert not connection.exists(str(outside_path))

    def test_handles_absolute_paths_correctly(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "bar.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"content")
        
        assert connection.exists(str(file_path))
        assert connection.exists(str(file_path.relative_to(tmp_path))) 