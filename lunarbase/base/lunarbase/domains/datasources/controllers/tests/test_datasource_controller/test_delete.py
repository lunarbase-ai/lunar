from unittest.mock import MagicMock
from lunarbase.domains.datasources.models import DataSourceType
import uuid


class TestDeleteDatasource:
    def test_delete_always_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        for ds_type in [DataSourceType.POSTGRESQL, DataSourceType.LOCAL_FILE]:
            mock_datasource = MagicMock()
            mock_datasource.type = ds_type
            mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
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
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource

        mock_datasource_controller.datasource_repository.delete.return_value = True

        result = mock_datasource_controller.delete(user_id, datasource_id)

        mock_datasource_controller.file_path_resolver.get_user_files_root_path.assert_not_called()
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
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        mock_datasource_controller.datasource_repository.delete.return_value = True
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.exists.side_effect = [True, False]

        result = mock_datasource_controller.delete(user_id, datasource_id)

        mock_datasource_controller.file_path_resolver.get_user_files_root_path.assert_called_once_with(user_id)
        mock_datasource_controller.file_storage_connection.exists.assert_any_call("/some/file1")
        mock_datasource_controller.file_storage_connection.exists.assert_any_call("/some/file2")
        mock_datasource_controller.file_storage_connection.delete.assert_called_once_with("/some/file1")
        mock_datasource_controller.file_storage_connection.remove_empty_directories.assert_called_once_with("/user/root")
        assert result is True 