#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest 
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.persistence.resolvers.local_files_path_resolver import LocalFilesPathResolver
from lunarbase.domains.datasources.repositories.local_files_datasource_repository import LocalFilesDataSourceRepository

@pytest.fixture
def connection(config):
    return LocalFilesStorageConnection(config)

@pytest.fixture
def path_resolver(config, connection):
    return LocalFilesPathResolver(connection, config)

@pytest.fixture
def datasource_repository(config, connection, path_resolver):
    return LocalFilesDataSourceRepository(connection, config, path_resolver) 