from abc import ABC, abstractmethod
from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.modeling.data_models import WorkflowModel
from lunarbase.config import LunarConfig
from typing import Optional, Dict, Any
from pathlib import Path
from lunarbase.modeling.base_repository import LunarRepository


class UserRepository(LunarRepository):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        super().__init__(connection, config)
