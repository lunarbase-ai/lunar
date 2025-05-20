import pytest 
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.persistence.resolvers.local_files_path_resolver import LocalFilesPathResolver
from lunarbase.domains.datasources.repositories.local_files_datasource_repository import LocalFilesDataSourceRepository
from lunarbase.modeling.datasources import LocalFile, DataSourceType
from pathlib import Path
import uuid

@pytest.fixture
def connection(config):
    return LocalFilesStorageConnection(config)

@pytest.fixture
def path_resolver(config, connection):
    return LocalFilesPathResolver(connection, config)

@pytest.fixture
def datasource_repository(config, connection, path_resolver):
    return LocalFilesDataSourceRepository(connection, config, path_resolver)


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

class TestUpdateDatasource:
    def test_update_datasource_returns_updated_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        # First create a datasource
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

        # Then update it
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
        
        # First create a valid datasource
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

        # Try to update with invalid data
        invalid_update = {
            "id": datasource_id,
            "name": "Invalid Update",
            # Missing required fields
        }

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.update(user_id, invalid_update)
        
        assert "Invalid datasource" in str(exc_info.value)

    def test_cant_update_to_unsupported_type(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        # First create a valid datasource
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

        # Try to update to an unsupported type
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
