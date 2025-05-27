#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from unittest.mock import MagicMock
from lunarbase.domains.datasources.controllers import DataSourceController

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