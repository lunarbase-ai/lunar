from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.persistence.repositories.base_repository import LunarRepository
from lunarbase.config import LunarConfig


class DatasourceRepository(LunarRepository):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        super().__init__(connection, config)

