from lunarbase.config import LunarConfig
from lunarbase.persistence import PersistenceLayer
# from lunarbase.utils import setup_logger
from lunarbase.domains.datasources.repositories import DataSourceRepository
from lunarbase.domains.datasources.models import DataSourceFilters
from typing import Optional, Union, Dict, List
from lunarbase.modeling.datasources import DataSource

class DataSourceController:
    def __init__(
            self, 
            config: LunarConfig, 
            datasource_repository: DataSourceRepository
        ):
        self._config = config
        self._datasource_repository = datasource_repository
        # self.__logger = setup_logger("datasource-controller")

    @property
    def config(self):
        return self._config

    @property
    def datasource_repository(self):
        return self._datasource_repository
    
    # get_datasource
    def index(self, user_id: str, filters: Optional[Union[DataSourceFilters, Dict]] = None) -> List[DataSource]:
        return self.datasource_repository.index(user_id, filters)
    
    # get_datasource
    def show(self, user_id: str, datasource_id: str) -> DataSource:
        return self.datasource_repository.show(user_id, datasource_id)
    
    # create_datasource
    def create(self, user_id: str, datasource: Dict) -> DataSource:
        return self.datasource_repository.create(user_id, datasource)
    
    # update_datasource
    def update(self, user_id: str, datasource: Dict) -> DataSource:
        return self.datasource_repository.update(user_id, datasource)
    