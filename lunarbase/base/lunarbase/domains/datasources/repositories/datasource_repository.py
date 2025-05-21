from lunarbase.persistence.connections.storage_connection import StorageConnection
from lunarbase.persistence.repositories.base_repository import LunarRepository
from lunarbase.config import LunarConfig
from abc import abstractmethod
from typing import Optional, Dict, List, Union
from lunarbase.modeling.datasources import DataSource
from lunarbase.domains.datasources.models import DataSourceFilters

class DataSourceRepository(LunarRepository):
    def __init__(self, connection: StorageConnection, config: LunarConfig):
        super().__init__(connection, config)


    @abstractmethod
    def index(self, user_id: str, filters: Optional[Union[DataSourceFilters, Dict]] = None) -> List[DataSource]:
        pass

    @abstractmethod
    def show(self, user_id: str, datasource_id: str) -> DataSource:
        pass
    
    @abstractmethod
    def create(self, user_id: str, datasource: Dict) -> DataSource:
        pass

    @abstractmethod
    def update(self, user_id: str, datasource: Dict) -> DataSource:
        pass

    @abstractmethod
    def delete(self, user_id: str, datasource_id: str) -> bool:
        pass
