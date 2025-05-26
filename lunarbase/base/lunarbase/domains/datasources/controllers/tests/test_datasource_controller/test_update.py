from unittest.mock import MagicMock
from lunarbase.domains.datasources.models import DataSourceType
import uuid


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