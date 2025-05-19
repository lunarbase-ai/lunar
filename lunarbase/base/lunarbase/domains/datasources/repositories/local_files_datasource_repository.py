from lunarbase.domains.datasources.repositories.datasource_repository import DatasourceRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.config import LunarConfig


class LocalFilesDatasourceRepository(DatasourceRepository):
    def __init__(self, connection: LocalFilesStorageConnection, config: LunarConfig):
        super().__init__(connection, config)
