#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import json
from pathlib import Path

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

        other_json_content = {"id": 3, "name": "other_item"}

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