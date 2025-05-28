#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

class TestRemoveEmptyDirectories:
    def test_removes_empty_subdirectories(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)

        root = tmp_path / "root"
        (root / "a" / "b").mkdir(parents=True)
        (root / "c").mkdir()
        (root / "d" / "e" / "f").mkdir(parents=True)

        file_path = root / "d" / "file.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("not empty")

        connection.remove_empty_directories(str(root))

        assert (root / "a" / "b").exists() is False
        assert (root / "a").exists() is True
        assert (root / "c").exists() is False
        assert (root / "d").exists() is True
        assert (root / "d" / "e" / "f").exists() is False
        assert (root / "d" / "e").exists() is True
        assert (root / "d" / "file.txt").exists() is True

    def test_does_not_remove_root_by_default(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        root = tmp_path / "root"
        root.mkdir()
        connection.remove_empty_directories(str(root))
        assert root.exists() is True

    def test_removes_root_if_remove_root_true(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        root = tmp_path / "root"
        root.mkdir()
        connection.remove_empty_directories(str(root), remove_root=True)
        assert root.exists() is False 