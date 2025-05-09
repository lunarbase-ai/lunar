import os.path
import zipfile
from pathlib import Path
from typing import Dict, Optional

from lunarbase.config import LunarConfig
from lunarbase.modeling.datasources import DataSource, DataSourceType
from lunarbase.modeling.datasources.attributes import LocalFile
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger

logger = setup_logger("datasource-controller")


class DatasourceController:
    def __init__(self, config: LunarConfig, persistence_layer: PersistenceLayer):
        self._config = config
        self._persistence_layer = persistence_layer
        self.__logger = setup_logger("datasource-controller")

    @property
    def config(self):
        return self._config

    @property
    def persistence_layer(self):
        return self._persistence_layer

    def get_datasource(self, user_id: str, filters: Optional[Dict] = None):
        def fltr(instance: Dict, filter: Dict):
            _all = True
            for key, value in filter.items():
                _filter = False
                if isinstance(value, dict):
                    _filter = fltr(instance.get(key), value)
                elif isinstance(value, list):
                    _filter = instance.get(key) in value
                elif instance.get(key) == value:
                    _filter = True
                _all = _all and _filter
                if not _all:
                    return False
            return _all

        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            return

        datasources = []
        for ds in datasource_root.glob("*.json"):
            ds_dict = self._persistence_layer.get_from_storage_as_dict(
                path=str(ds)
            )
            if filters is not None:
                accept = fltr(ds_dict, filters)
                if not accept:
                    continue
            try:
                ds = DataSource.polymorphic_validation(ds_dict)
            except ValueError:
                self.__logger.warn(f"Invalid datasource for user {user_id} at {str(ds)}")
                continue
            if ds is not None:
                datasources.append(ds)
        return datasources

    def create_datasource(self, user_id: str, datasource: Dict):
        try:
            datasource = DataSource.polymorphic_validation(datasource)
        except ValueError as e:
            raise ValueError(f"Invalid datasource: {str(e)}")

        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            datasource_root.mkdir(parents=True, exist_ok=True)

        datasource_path = Path(datasource_root, f"{datasource.id}.json")
        self._persistence_layer.save_to_storage_as_json(
            path=str(datasource_path), data=datasource.model_dump()
        )

        return datasource

    def update_datasource(self, user_id: str, datasource: Dict):
        try:
            datasource = DataSource.polymorphic_validation(datasource)
        except ValueError as e:
            raise ValueError(f"Invalid datasource: {str(e)}")

        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            raise ValueError(f"Current user has not datasources defined!")

        datasource_path = Path(datasource_root, f"{datasource.id}.json")
        if not datasource_path.exists():
            raise ValueError(f"Datasource {datasource.id} does not exist!")

        self._persistence_layer.save_to_storage_as_json(
            path=str(datasource_path), data=datasource.model_dump()
        )

        return datasource

    def upload_local_file(self, user_id: str, datasource_id: str, file):
        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            raise ValueError(f"Current user has no datasources defined!")

        datasource_path = Path(datasource_root, f"{datasource_id}.json")
        if not datasource_path.exists():
            raise ValueError(f"Datasource {datasource_id} does not exist!")

        ds_dict = self._persistence_layer.get_from_storage_as_dict(
            path=str(datasource_path)
        )
        try:
            ds = DataSource.polymorphic_validation(ds_dict)
        except ValueError as e:
            raise e

        if ds.type != DataSourceType.LOCAL_FILE:
            raise ValueError(f"Datasource {datasource_id} is not a local file datasource!")

        files_root = Path(self._persistence_layer.get_user_file_root(user_id))
        if not files_root.exists():
            files_root.mkdir(parents=True, exist_ok=True)
        file_location_path = self._persistence_layer.save_file_to_storage(
            path=str(files_root), file=file
        )
        file_path = os.path.join(file_location_path, file.filename)
        if zipfile.is_zipfile(file_path):
            ds.connection_attributes.files = []
            file_paths = self._persistence_layer.extract_zip_and_get_file_paths(file_path)
            self._persistence_layer.delete(file_path)
            for file_path in file_paths:
                local_file = LocalFile(
                    file_name=file_path,
                )
                ds.connection_attributes.files.append(local_file)
        else:
            local_file = LocalFile(
                file_name=file_path
            )
            ds.connection_attributes.files.append(local_file)
        self._persistence_layer.save_to_storage_as_json(
            path=str(datasource_path), data=ds.model_dump()
        )

        self.__logger.info(f"Uploaded file {file.filename}")
        return ds.id

    def remove_empty_directories(self, directory, remove_root=False):
        for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
            if not filenames and not dirnames:
                if dirpath == directory and not remove_root:
                    continue
                try:
                    os.rmdir(dirpath)
                    print(f"Removed empty directory: {dirpath}")
                except Exception as e:
                    print(f"Failed to remove {dirpath}: {e}")


    def delete_datasource(self, user_id: str, datasource_id: str):
        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            raise ValueError(f"Current user has not datasources defined!")

        datasource_path = Path(datasource_root, f"{datasource_id}.json")
        if not datasource_path.exists():
            raise ValueError(f"Datasource {datasource_id} does not exist!")

        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            return

        ds_path = Path(datasource_root, f"{datasource_id}.json")
        if not Path(ds_path).exists():
            raise ValueError(f"Datasource {datasource_id} does not exist!")

        ds_dict = self._persistence_layer.get_from_storage_as_dict(
            path=str(ds_path)
        )
        try:
            ds = DataSource.polymorphic_validation(ds_dict)
        except ValueError:
            raise ValueError(f"Invalid datasource for user {user_id} at {str(ds_path)}")

        files_root = Path(self._persistence_layer.get_user_file_root(user_id))
        if ds.type == DataSourceType.LOCAL_FILE:
            _files = ds.to_component_input(base_path=str(files_root))
            for _file in _files:
                if Path(_file.path).exists():
                    self._persistence_layer.delete(str(_file.path))
            self.remove_empty_directories(files_root)

        self._persistence_layer.delete(path=str(datasource_path))

        return True

    @staticmethod
    def get_datasource_types():
        datasources = []
        for e in DataSourceType:
            datasources.append(
                {
                    "id": e.name,
                    "name": e.name.replace("_", " "),
                    "connectionAttributes": e.expected_connection_attributes()[1]
                }
            )
        return datasources