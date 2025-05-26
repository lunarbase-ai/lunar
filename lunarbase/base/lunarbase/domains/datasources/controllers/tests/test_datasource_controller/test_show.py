from unittest.mock import MagicMock
import uuid


class TestShowDatasource:
    def test_show_delegates_to_repository(self, mock_datasource_controller, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_id = str(uuid.uuid4())
        mock_datasource = MagicMock()
        mock_datasource_controller.datasource_repository.show.return_value = mock_datasource

        result = mock_datasource_controller.show(user_id, datasource_id)

        mock_datasource_controller.datasource_repository.show.assert_called_once_with(user_id, datasource_id)
        assert result == mock_datasource 