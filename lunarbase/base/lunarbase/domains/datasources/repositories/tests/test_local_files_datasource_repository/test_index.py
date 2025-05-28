#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from lunarbase.domains.datasources.models import DataSourceFilters, DataSourceType
import uuid
from pathlib import Path

class TestIndexDatasource:
    def test_index_returns_empty_list_when_no_datasources(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        result = datasource_repository.index(user_id)
        assert result == []

    def test_index_returns_single_valid_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
            "description": "Test Datasource",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource_dict)
        result = datasource_repository.index(user_id)

        assert len(result) == 1
        assert result[0].id == datasource_dict["id"]
        assert result[0].name == datasource_dict["name"]
        assert result[0].description == datasource_dict["description"]
        assert result[0].type == datasource_dict["type"]
        assert result[0].connection_attributes.model_dump() == datasource_dict["connection_attributes"]

    def test_index_returns_multiple_valid_datasources(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)
        result = datasource_repository.index(user_id)

        assert len(result) == 2
        result_ids = [ds.id for ds in result]
        assert datasource1["id"] in result_ids
        assert datasource2["id"] in result_ids

    def test_index_skips_invalid_datasource(self, datasource_repository, config, connection, path_resolver):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        valid_datasource = {
            "id": str(uuid.uuid4()),
            "name": "Valid Datasource",
            "description": "Valid Datasource",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        invalid_datasource = {
            "id": str(uuid.uuid4()),
            "name": "Invalid Datasource",
        }

        datasource_repository.create(user_id, valid_datasource)

        invalid_path = path_resolver.get_user_datasource_path(invalid_datasource["id"], user_id)
        connection.save_dict_as_json(invalid_path, invalid_datasource)

        result = datasource_repository.index(user_id)

        assert len(result) == 1
        assert result[0].id == valid_datasource["id"]

    def test_index_filters_by_id(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = DataSourceFilters(id=uuid.UUID(datasource1["id"]))
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 1
        assert result[0].id == datasource1["id"]

    def test_index_filters_by_name(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = DataSourceFilters(name="Test Datasource 1")
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 1
        assert result[0].name == "Test Datasource 1"

    def test_index_filters_by_type(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = DataSourceFilters(type=DataSourceType.LOCAL_FILE)
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 2
        assert all(ds.type == DataSourceType.LOCAL_FILE for ds in result)

    def test_index_filters_by_multiple_criteria(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = DataSourceFilters(
            id=uuid.UUID(datasource1["id"]),
            name="Test Datasource 1",
            type=DataSourceType.LOCAL_FILE
        )
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 1
        assert result[0].id == datasource1["id"]
        assert result[0].name == "Test Datasource 1"
        assert result[0].type == DataSourceType.LOCAL_FILE

    def test_index_filters_by_dict_id(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = {"id": datasource1["id"]}
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 1
        assert result[0].id == datasource1["id"]

    def test_index_filters_by_dict_name(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = {"name": "Test Datasource 1"}
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 1
        assert result[0].name == "Test Datasource 1"

    def test_index_filters_by_dict_type(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = {"type": "LOCAL_FILE"}
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 2
        assert all(ds.type == DataSourceType.LOCAL_FILE for ds in result)

    def test_index_filters_by_dict_multiple_criteria(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource1 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 1",
            "description": "Test Datasource 1",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource2 = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource 2",
            "description": "Test Datasource 2",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource1)
        datasource_repository.create(user_id, datasource2)

        filters = {
            "id": datasource1["id"],
            "name": "Test Datasource 1",
            "type": "LOCAL_FILE"
        }
        result = datasource_repository.index(user_id, filters)

        assert len(result) == 1
        assert result[0].id == datasource1["id"]
        assert result[0].name == "Test Datasource 1"
        assert result[0].type == DataSourceType.LOCAL_FILE

    def test_index_filters_by_invalid_dict(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
            "description": "Test Datasource",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource)

        filters = {"type": "INVALID_TYPE"}
        result = datasource_repository.index(user_id, filters)
        assert len(result) == 0 

        filters = {"invalid_field": "value", "name": "Test Datasource"}
        result = datasource_repository.index(user_id, filters)
        assert len(result) == 1
        assert result[0].id == datasource["id"] 