import pytest
from lunarbase.domains.datasources.controllers import DataSourceController
from lunarbase.modeling.datasources import DataSourceType
import uuid
from unittest.mock import MagicMock


@pytest.fixture
def mock_datasource_controller(lunar_context):
    mock_repository = MagicMock()
    mock_file_storage_connection = MagicMock()
    mock_file_path_resolver = MagicMock()
    return DataSourceController(
        config=lunar_context.lunar_config,
        datasource_repository=mock_repository,
        file_storage_connection=mock_file_storage_connection,
        file_path_resolver=mock_file_path_resolver
    )


class TestCreateDatasource:
    def test_create_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
            "description": "A test datasource",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        
        mock_datasource = MagicMock()
        mock_datasource_controller.datasource_repository.create.return_value = mock_datasource

        result = mock_datasource_controller.create(user_id, datasource_dict)

        mock_datasource_controller.datasource_repository.create.assert_called_once_with(user_id, datasource_dict)

        assert result == mock_datasource


class TestShowDatasource:
    def test_show_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        mock_datasource = MagicMock()
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource

        result = mock_datasource_controller.show(user_id, datasource_id)

        mock_datasource_controller.datasource_repository.show.assert_called_once_with(user_id, datasource_id)
        assert result == mock_datasource


class TestIndexDatasource:
    def test_index_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        filters = {"name": "Test"}
        mock_datasources = [MagicMock(), MagicMock()]
        mock_datasource_controller.datasource_repository.index.return_value = mock_datasources

        result = mock_datasource_controller.index(user_id, filters)

        mock_datasource_controller.datasource_repository.index.assert_called_once_with(user_id, filters)
        assert result == mock_datasources


class TestUpdateDatasource:
    def test_update_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Updated Datasource",
            "description": "An updated datasource",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }
        mock_datasource = MagicMock()
        mock_datasource_controller.datasource_repository.update.return_value = mock_datasource

        result = mock_datasource_controller.update(user_id, datasource_dict)

        mock_datasource_controller.datasource_repository.update.assert_called_once_with(user_id, datasource_dict)
        assert result == mock_datasource


class TestIndexTypes:
    def test_index_types_returns_expected_types(self, mock_datasource_controller):
        result = mock_datasource_controller.index_types()

        assert isinstance(result, list)
        for e in DataSourceType:
            found = any(
                item["id"] == e.name and
                item["name"] == e.name.replace("_", " ") and
                item["connectionAttributes"] == e.expected_connection_attributes()[1]
                for item in result
            )
            assert found, f"Type {e.name} not found in result"


class TestDeleteDatasource:
    def test_delete_always_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        for ds_type in [DataSourceType.POSTGRESQL, DataSourceType.LOCAL_FILE]:
            mock_datasource = MagicMock()
            mock_datasource.type = ds_type
            mock_datasource_controller.show = MagicMock(return_value=mock_datasource)
            mock_datasource_controller.datasource_repository.delete.return_value = True

            mock_datasource_controller.datasource_repository.delete.reset_mock()
            result = mock_datasource_controller.delete(user_id, datasource_id)
            mock_datasource_controller.datasource_repository.delete.assert_called_once_with(user_id, datasource_id)
            assert result is True

    def test_delete_non_local_file_does_not_call_file_removal(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())

        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.POSTGRESQL
        mock_datasource_controller.show = MagicMock(return_value=mock_datasource)

        mock_datasource_controller.datasource_repository.delete.return_value = True

        result = mock_datasource_controller.delete(user_id, datasource_id)

        mock_datasource_controller.file_path_resolver.get_user_file_root.assert_not_called()
        mock_datasource_controller.file_storage_connection.exists.assert_not_called()
        mock_datasource_controller.file_storage_connection.delete.assert_not_called()
        mock_datasource_controller.file_storage_connection.remove_empty_directories.assert_not_called()
        assert result is True

    def test_delete_local_file_removes_files_and_directories(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())

        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.LOCAL_FILE

        file1 = MagicMock(path="/some/file1")
        file2 = MagicMock(path="/some/file2")

        mock_datasource.to_component_input.return_value = [file1, file2]
        mock_datasource_controller.show = MagicMock(return_value=mock_datasource)
        mock_datasource_controller.datasource_repository.delete.return_value = True
        mock_datasource_controller.file_path_resolver.get_user_file_root.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.exists.side_effect = [True, False]

        result = mock_datasource_controller.delete(user_id, datasource_id)

        mock_datasource_controller.file_path_resolver.get_user_file_root.assert_called_once_with(user_id)
        mock_datasource_controller.file_storage_connection.exists.assert_any_call("/some/file1")
        mock_datasource_controller.file_storage_connection.exists.assert_any_call("/some/file2")
        mock_datasource_controller.file_storage_connection.delete.assert_called_once_with("/some/file1")
        mock_datasource_controller.file_storage_connection.remove_empty_directories.assert_called_once_with("/user/root")
        assert result is True