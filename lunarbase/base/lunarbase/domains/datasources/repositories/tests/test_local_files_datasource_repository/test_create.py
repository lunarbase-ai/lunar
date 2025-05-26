import pytest
from lunarbase.domains.datasources.models import DataSourceType
import uuid
from pathlib import Path

class TestCreateDatasource:
    def test_create_datasource_returns_datasource(self, datasource_repository, config):
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

        saved_datasource = datasource_repository.create(user_id, datasource_dict)

        assert saved_datasource.id == datasource_dict["id"]
        assert saved_datasource.name == datasource_dict["name"]
        assert saved_datasource.description == datasource_dict["description"]
        assert saved_datasource.type == datasource_dict["type"]
        assert saved_datasource.connection_attributes.model_dump() == datasource_dict["connection_attributes"]

    def test_create_datasource_in_correct_path(self, datasource_repository, config, path_resolver):
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

        path = path_resolver.get_user_datasource_path(datasource_dict["id"], user_id)

        assert Path(path).exists()

    def test_cant_create_datasource_with_invalid_data(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        invalid_datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.create(user_id, invalid_datasource_dict)
        
        assert "Invalid datasource" in str(exc_info.value)

    def test_cant_create_postgresql_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        unsupported_datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
            "description": "Test Datasource",
            "type": DataSourceType.POSTGRESQL,
            "connection_attributes": {
                "url": "postgresql://test:test@localhost:5432/test"
            }
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.create(user_id, unsupported_datasource_dict)
        
        expected_error = f"Unsupported datasource type: {DataSourceType.POSTGRESQL}"
        assert str(exc_info.value) == expected_error

    def test_cant_create_sparql_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        sparql_datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
            "description": "Test Datasource",
            "type": DataSourceType.SPARQL,
            "connection_attributes": {
                "endpoint": "http://example.org/sparql"
            }
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.create(user_id, sparql_datasource_dict)
        
        expected_error = f"Unsupported datasource type: {DataSourceType.SPARQL}"
        assert str(exc_info.value) == expected_error 