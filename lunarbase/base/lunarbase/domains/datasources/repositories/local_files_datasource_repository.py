from lunarbase.domains.datasources.repositories.datasource_repository import DataSourceRepository
from lunarbase.persistence.connections.local_files_storage_connection import LocalFilesStorageConnection
from lunarbase.config import LunarConfig
from typing import Optional, Dict, List
from lunarbase.modeling.datasources import DataSource, DataSourceType
from lunarbase.persistence.resolvers.file_path_resolver import FilePathResolver
from lunarbase.domains.datasources.models import DataSourceFilters

class LocalFilesDataSourceRepository(DataSourceRepository):
    UNSUPPORTED_DATASOURCE_TYPES = [
        DataSourceType.POSTGRESQL,
        DataSourceType.SPARQL,
    ]

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
    
    def index(self, user_id: str, filters: Optional[DataSourceFilters] = None) -> List[DataSource]:
        pass

    def show(self, user_id: str, datasource_id: str) -> DataSource:
        datasource_path = self.path_resolver.get_user_datasource_path(datasource_id, user_id)

        if not self.connection.exists(datasource_path):
            raise ValueError(f"Datasource {datasource_id} does not exist!")

        datasource_dict = self.connection.get_as_dict_from_json(datasource_path)
        return self._validate_datasource(datasource_dict)

    def create(self, user_id: str, datasource: Dict) -> DataSource:
        datasource = self._validate_datasource(datasource)

        datasource_path = self.path_resolver.get_user_datasource_path(datasource.id, user_id)

        self.connection.save_dict_as_json(datasource_path, datasource.model_dump())

        return datasource

    def update(self, user_id: str, datasource: Dict) -> DataSource:
        datasource = self._validate_datasource(datasource)
        datasource_path = self.path_resolver.get_user_datasource_path(datasource.id, user_id)

        if not self.connection.exists(datasource_path):
            raise ValueError(f"Datasource {datasource.id} does not exist!")

        self.connection.save_dict_as_json(datasource_path, datasource.model_dump())

        return datasource

    def delete(self, user_id: str, datasource_id: str) -> bool:
        pass


    def _validate_datasource(self, datasource: Dict) -> DataSource:
        try:
            datasource = DataSource.polymorphic_validation(datasource)
        except ValueError as e:
            raise ValueError(f"Invalid datasource: {str(e)}")
        
        if datasource.type in self.UNSUPPORTED_DATASOURCE_TYPES:
            raise ValueError(f"Unsupported datasource type: {datasource.type}")
        
        return datasource
