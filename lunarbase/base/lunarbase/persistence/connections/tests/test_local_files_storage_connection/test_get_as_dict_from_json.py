#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

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