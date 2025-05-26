import pytest
from unittest.mock import MagicMock, patch
from lunarbase.domains.datasources.models import DataSourceType, LocalFile, LocalFileConnectionAttributes
import uuid


class TestUploadLocalFile:
    def test_upload_local_file_regular_file(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.LOCAL_FILE
        mock_datasource.id = datasource_id
        mock_datasource.connection_attributes = LocalFileConnectionAttributes(files=[])
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.save_file.return_value = "/user/root/test.txt"
        
        result = mock_datasource_controller.upload_local_file(user_id, datasource_id, mock_file)
        
        mock_datasource_controller.datasource_repository.show.assert_called_once_with(user_id, datasource_id)
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.assert_called_once_with(user_id)
        mock_datasource_controller.file_storage_connection.save_file.assert_called_once_with(
            path="/user/root", file=mock_file
        )
        assert len(mock_datasource.connection_attributes.files) == 1
        assert mock_datasource.connection_attributes.files[0].file_name == "/user/root/test.txt"
        assert result == datasource_id

    def test_upload_local_file_zip_file(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.LOCAL_FILE
        mock_datasource.id = datasource_id
        mock_datasource.connection_attributes = LocalFileConnectionAttributes(files=[])
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        
        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.save_file.return_value = "/user/root/test.zip"
        
        with patch('zipfile.is_zipfile', return_value=True):
            mock_datasource_controller.file_storage_connection.extract_zip.return_value = [
                "/user/root/extracted1.txt",
                "/user/root/extracted2.txt"
            ]
            
            result = mock_datasource_controller.upload_local_file(user_id, datasource_id, mock_file)
            
            mock_datasource_controller.datasource_repository.show.assert_called_once_with(user_id, datasource_id)
            mock_datasource_controller.file_path_resolver.get_user_files_root_path.assert_called_once_with(user_id)
            mock_datasource_controller.file_storage_connection.save_file.assert_called_once_with(
                path="/user/root", file=mock_file
            )
            mock_datasource_controller.file_storage_connection.extract_zip.assert_called_once_with("/user/root/test.zip")
            mock_datasource_controller.file_storage_connection.delete.assert_called_once_with("/user/root/test.zip")
            
            assert len(mock_datasource.connection_attributes.files) == 2
            file_names = {file.file_name for file in mock_datasource.connection_attributes.files}
            assert "/user/root/extracted1.txt" in file_names
            assert "/user/root/extracted2.txt" in file_names
            assert result == datasource_id

    def test_upload_local_file_invalid_datasource_type(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.POSTGRESQL
        mock_datasource.connection_attributes = LocalFileConnectionAttributes(files=[])
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        with pytest.raises(ValueError, match=f"Datasource {datasource_id} is not a local file datasource!"):
            mock_datasource_controller.upload_local_file(user_id, datasource_id, mock_file)

    def test_upload_local_file_preserves_existing_files(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        existing_file = LocalFile(file_name="/user/root/existing.txt")
        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.LOCAL_FILE
        mock_datasource.id = datasource_id
        mock_datasource.connection_attributes = LocalFileConnectionAttributes(files=[existing_file])
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.save_file.return_value = "/user/root/test.txt"
        
        result = mock_datasource_controller.upload_local_file(user_id, datasource_id, mock_file)
        
        assert len(mock_datasource.connection_attributes.files) == 2
        assert mock_datasource.connection_attributes.files[0].file_name == "/user/root/existing.txt"
        assert mock_datasource.connection_attributes.files[1].file_name == "/user/root/test.txt"
        assert result == datasource_id

    def test_upload_local_file_handles_dict_connection_attributes(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.LOCAL_FILE
        mock_datasource.id = datasource_id
        mock_datasource.connection_attributes = {"files": [{"file_name": "/user/root/existing.txt"}]}
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.save_file.return_value = "/user/root/test.txt"
        
        result = mock_datasource_controller.upload_local_file(user_id, datasource_id, mock_file)
        
        assert len(mock_datasource.connection_attributes.files) == 2
        assert mock_datasource.connection_attributes.files[0].file_name == "/user/root/existing.txt"
        assert mock_datasource.connection_attributes.files[1].file_name == "/user/root/test.txt"
        assert result == datasource_id

    def test_upload_local_file_skips_duplicate_files(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        
        existing_file = LocalFile(file_name="/user/root/test.txt")
        mock_datasource = MagicMock()
        mock_datasource.type = DataSourceType.LOCAL_FILE
        mock_datasource.id = datasource_id
        mock_datasource.connection_attributes = LocalFileConnectionAttributes(files=[existing_file])
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource
        
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        mock_datasource_controller.file_path_resolver.get_user_files_root_path.return_value = "/user/root"
        mock_datasource_controller.file_storage_connection.save_file.return_value = "/user/root/test.txt"
        
        result = mock_datasource_controller.upload_local_file(user_id, datasource_id, mock_file)
        
        assert len(mock_datasource.connection_attributes.files) == 1
        assert mock_datasource.connection_attributes.files[0].file_name == "/user/root/test.txt"
        assert result == datasource_id 