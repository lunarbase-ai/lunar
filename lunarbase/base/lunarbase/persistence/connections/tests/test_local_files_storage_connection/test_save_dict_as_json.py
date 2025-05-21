#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import json
from pathlib import Path

class TestSaveDictAsJson:
    def test_creates_json_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_path = tmp_path / "foo" / "data.json"
        data = {"a": 1, "b": [2, 3]}
        result_path = connection.save_dict_as_json(str(file_path.relative_to(tmp_path)), data)
        assert Path(result_path).exists()
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

        dir_path = tmp_path / "foo" / "data.json"
        dir_path.mkdir(parents=True)
        with pytest.raises(ValueError, match="already exists and is not a file"):
            connection.save_dict_as_json(str(dir_path.relative_to(tmp_path)), {"fail": True})

    def test_raises_value_error_on_invalid_json_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)

        outside_path = Path("/should_not_exist.json")
        with pytest.raises(ValueError, match="Problem encountered with path"):
            connection.save_dict_as_json(str(outside_path), {"fail": True}) 