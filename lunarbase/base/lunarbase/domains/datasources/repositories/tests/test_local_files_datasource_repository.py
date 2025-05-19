import pytest 
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.persistence.resolvers.local_files_path_resolver import LocalFilesPathResolver
from lunarbase.domains.datasources.repositories.local_files_datasource_repository import LocalFilesDataSourceRepository
from lunarbase.modeling.datasources import LocalFile, DataSourceType
from pathlib import Path
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
        datasource = LocalFile(
            name="Test Datasource",
            description="Test Datasource",
            type=DataSourceType.LOCAL_FILE,
            connection_attributes={
                "files": []
            }
        )   

        saved_datasource = datasource_repository.create(user_id, datasource)

        assert saved_datasource.id == datasource.id
        assert saved_datasource.name == datasource.name
        assert saved_datasource.description == datasource.description
        assert saved_datasource.type == datasource.type
        assert saved_datasource.connection_attributes == datasource.connection_attributes

    def test_create_datasource_in_correct_path(self, datasource_repository, config, path_resolver):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource = LocalFile(
            name="Test Datasource",
            description="Test Datasource",
            type=DataSourceType.LOCAL_FILE,
            connection_attributes={
                "files": []
            }
        )

        datasource_repository.create(user_id, datasource)

        path = path_resolver.get_user_datasource_path(datasource.id, user_id)

        assert Path(path).exists()
