import pytest
from lunarbase.domains.datasources.models import DataSourceType
import uuid

class TestUpdateDatasource:
    def test_update_datasource_returns_updated_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        initial_datasource = {
            "id": datasource_id,
            "name": "Initial Datasource",
            "description": "Initial Description",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource_repository.create(user_id, initial_datasource)

        updated_datasource = {
            "id": datasource_id,
            "name": "Updated Datasource",
            "description": "Updated Description",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": [{
                    "file_name": "new_file.txt",
                    "file_type": "text/plain"
                }]
            }
        }

        result = datasource_repository.update(user_id, updated_datasource)

        assert result.id == updated_datasource["id"]
        assert result.name == updated_datasource["name"]
        assert result.description == updated_datasource["description"]
        assert result.type == updated_datasource["type"]
        assert result.connection_attributes.model_dump() == updated_datasource["connection_attributes"]

    def test_cant_update_nonexistent_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        nonexistent_datasource = {
            "id": str(uuid.uuid4()),
            "name": "Nonexistent Datasource",
            "description": "This should fail",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.update(user_id, nonexistent_datasource)
        
        assert f"Datasource {nonexistent_datasource['id']} does not exist!" in str(exc_info.value)

    def test_cant_update_with_invalid_data(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
            
        initial_datasource = {
            "id": datasource_id,
            "name": "Initial Datasource",
            "description": "Initial Description",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource_repository.create(user_id, initial_datasource)

        invalid_update = {
            "id": datasource_id,
            "name": "Invalid Update",
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.update(user_id, invalid_update)
        
        assert "Invalid datasource" in str(exc_info.value)

    def test_cant_update_to_unsupported_type(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        initial_datasource = {
            "id": datasource_id,
            "name": "Initial Datasource",
            "description": "Initial Description",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        datasource_repository.create(user_id, initial_datasource)

        unsupported_update = {
            "id": datasource_id,
            "name": "Unsupported Update",
            "description": "Trying to change type",
            "type": DataSourceType.POSTGRESQL,
            "connection_attributes": {
                "url": "postgresql://test:test@localhost:5432/test"
            }
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.update(user_id, unsupported_update)
        
        expected_error = f"Unsupported datasource type: {DataSourceType.POSTGRESQL}"
        assert str(exc_info.value) == expected_error 