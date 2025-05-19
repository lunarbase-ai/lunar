from lunarbase.domains.datasources.repositories.datasource_repository import DataSourceRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.config import LunarConfig
from typing import Optional, Dict, List
from lunarbase.modeling.datasources import DataSource, DataSourceType
from lunarbase.persistence.resolvers.file_path_resolver import FilePathResolver

class LocalFilesDataSourceRepository(DataSourceRepository):
    def __init__(
            self, 
            connection: LocalFilesStorageConnection, 
            config: LunarConfig,
            path_resolver: FilePathResolver
        ):
        super().__init__(connection, config)
        self._path_resolver = path_resolver

    @property
    def path_resolver(self) -> FilePathResolver:
        return self._path_resolver
    
    def index(self, user_id: str, filters: Optional[Dict] = None) -> List[DataSource]:
        pass

    def show(self, user_id: str, datasource_id: str) -> DataSource:
        pass

    def create(self, user_id: str, datasource: DataSource) -> DataSource:
        try:
            datasource_dict = datasource.model_dump()
            datasource = DataSource.polymorphic_validation(datasource_dict)
        except ValueError as e:
            raise ValueError(f"Invalid datasource: {str(e)}")
        
        UNSUPPORTED_DATASOURCE_TYPES = [
            DataSourceType.POSTGRESQL,
            DataSourceType.SPARQL,
        ]

        if datasource.type in UNSUPPORTED_DATASOURCE_TYPES:
            raise ValueError(f"Unsupported datasource type: {datasource.type}")

        datasource_path = self.path_resolver.get_user_datasource_path(datasource.id, user_id)

        self.connection.save_dict_as_json(datasource_path, datasource.model_dump())

        return datasource

    def update(self, user_id: str, datasource: DataSource) -> DataSource:
        pass

    def delete(self, user_id: str, datasource_id: str) -> bool:
        pass
