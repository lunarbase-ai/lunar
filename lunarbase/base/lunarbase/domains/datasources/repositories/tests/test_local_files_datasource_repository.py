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
