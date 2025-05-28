#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import os
from pathlib import Path

class TestResolvePath:
    def test_resolves_relative_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        rel_path = "foo/bar.txt"
        resolved = connection._resolve_path(rel_path)
        assert str(resolved) == str(tmp_path / "foo" / "bar.txt")
        assert resolved.is_absolute()

    def test_resolves_absolute_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        abs_path = tmp_path / "foo" / "bar.txt"
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        resolved = connection._resolve_path(str(abs_path))
        assert resolved == abs_path.resolve()

    def test_raises_value_error_on_absolute_path_outside_of_base(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)

        outside_path = Path(os.path.abspath(os.sep)) / "should_not_exist.txt"
        with pytest.raises(ValueError, match="outside of the base path"):
            connection._resolve_path(str(outside_path))

    def test_resolves_path_no_base(self, connection):
        connection._lunar_base_path = None
        rel_path = "foo/bar.txt"
        cwd = Path(".").resolve()
        resolved = connection._resolve_path(rel_path)
        assert str(resolved) == str(cwd / "foo" / "bar.txt")
        assert resolved.is_absolute() 