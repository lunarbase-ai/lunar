#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from lunarbase.config import LunarConfig
from lunarbase.domains.datasources.repositories import DataSourceRepository
from typing import Optional, Union, Dict, List
from lunarbase.domains.datasources.models import (
    DataSourceFilters, LocalFile, LocalFileConnectionAttributes, DataSource, DataSourceType
)
from lunarbase.persistence.connections import LocalFilesStorageConnection
from lunarbase.persistence.resolvers import FilePathResolver
import zipfile
from lunarbase.utils import setup_logger
from fastapi import UploadFile

class DataSourceController:
    def __init__(
            self, 
            config: LunarConfig, 
            datasource_repository: DataSourceRepository,
            file_storage_connection: LocalFilesStorageConnection,
            file_path_resolver: FilePathResolver
        ):
        self._config = config
        self._datasource_repository = datasource_repository
        self._file_storage_connection = file_storage_connection
        self._file_path_resolver = file_path_resolver
        self.__logger = setup_logger("datasource-controller")

    @property
    def config(self):
        return self._config

    @property
    def datasource_repository(self):
        return self._datasource_repository
    
    @property
    def file_storage_connection(self):
        return self._file_storage_connection
    
    @property
    def file_path_resolver(self):
        return self._file_path_resolver

    def index(self, user_id: str, filters: Optional[Union[DataSourceFilters, Dict]] = None) -> List[DataSource]:
        return self.datasource_repository.index(user_id, filters)

    def show(self, user_id: str, datasource_id: str) -> DataSource:
        return self.datasource_repository.show(user_id, datasource_id)

    def create(self, user_id: str, datasource: Dict) -> DataSource:
        return self.datasource_repository.create(user_id, datasource)
    
    def update(self, user_id: str, datasource: Dict) -> DataSource:
        return self.datasource_repository.update(user_id, datasource)
    
    def delete(self, user_id: str, datasource_id: str) -> bool:
        datasource = self.datasource_repository.show(user_id, datasource_id)

        if datasource.type == DataSourceType.LOCAL_FILE:
            files_root = self.file_path_resolver.get_user_files_root_path(user_id)
            _files = datasource.to_component_input(base_path=files_root)
            for _file in _files:
                if self.file_storage_connection.exists(_file.path):
                    self.file_storage_connection.delete(_file.path)
            self.file_storage_connection.remove_empty_directories(files_root)

        return self.datasource_repository.delete(user_id, datasource_id)
    
    def upload_local_file(self, user_id: str, datasource_id: str, file: UploadFile) -> str:
        datasource = self.datasource_repository.show(user_id, datasource_id)

        if datasource.type != DataSourceType.LOCAL_FILE:
            raise ValueError(f"Datasource {datasource_id} is not a local file datasource!")
        
        files_root = self.file_path_resolver.get_user_files_root_path(user_id)
        file_path = self.file_storage_connection.save_file(path=files_root, file=file)

        if not isinstance(datasource.connection_attributes, LocalFileConnectionAttributes):
            datasource.connection_attributes = LocalFileConnectionAttributes(
                files=datasource.connection_attributes.get('files', []) if isinstance(datasource.connection_attributes, dict) else []
            )

        files_to_add = set()
        if zipfile.is_zipfile(file_path):
            extracted_files = self.file_storage_connection.extract_zip(file_path)
            self.file_storage_connection.delete(file_path)
            files_to_add = set(extracted_files)
        else:
            files_to_add = {file_path}

        existing_files = {file.file_name for file in datasource.connection_attributes.files}
        for file_path in files_to_add - existing_files:
            datasource.connection_attributes.files.append(LocalFile(file_name=file_path))

        self.datasource_repository.update(user_id, datasource.model_dump())
        self.__logger.info(f"Uploaded file {file.filename}")

        return datasource.id
        
    def index_types(self) -> List[Dict]:
        types = []
        for e in DataSourceType:
            types.append(
                {
                    "id": e.name,
                    "name": e.name.replace("_", " "),
                    "connectionAttributes": e.expected_connection_attributes()[1]   
                }
            )
        return types
