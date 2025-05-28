#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from unittest.mock import MagicMock
from lunarbase.domains.datasources.models import DataSourceType
import uuid


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