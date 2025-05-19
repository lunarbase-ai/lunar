from lunarbase.domains.datasources.repositories.datasource_repository import DataSourceRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.config import LunarConfig
from typing import Optional, Dict, List
from lunarbase.modeling.datasources import DataSource


class LocalFilesDataSourceRepository(DataSourceRepository):
    def __init__(self, connection: LocalFilesStorageConnection, config: LunarConfig):
        super().__init__(connection, config)

    def index(self, user_id: str, filters: Optional[Dict] = None) -> List[DataSource]:
        pass

    def show(self, user_id: str, datasource_id: str) -> DataSource:
        pass

    def create(self, user_id: str, datasource: DataSource) -> DataSource:
        pass

    def update(self, user_id: str, datasource: DataSource) -> DataSource:
        pass

    def delete(self, user_id: str, datasource_id: str) -> bool:
        pass
