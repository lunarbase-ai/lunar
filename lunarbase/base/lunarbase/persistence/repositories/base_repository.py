#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC
from pathlib import Path
from typing import Dict, Any
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.config import LunarConfig


class LunarRepository(ABC):
    """Base repository class that provides common functionality for all repositories."""
    
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        self._connection = connection.connect()
        self._config = config
    
    @property
    def connection(self):
        return self._connection
    
    @property
    def config(self):
        return self._config 