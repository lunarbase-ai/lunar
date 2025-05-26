from unittest.mock import MagicMock


class TestIndexDatasource:
    def test_index_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        filters = {"name": "Test"}
        mock_datasources = [MagicMock(), MagicMock()]
        mock_datasource_controller.datasource_repository.index.return_value = mock_datasources

        result = mock_datasource_controller.index(user_id, filters)

        mock_datasource_controller.datasource_repository.index.assert_called_once_with(user_id, filters)
        assert result == mock_datasources 