from pathlib import Path
from typing import Union, Dict, Optional

from lunarbase import LunarConfig
from lunarbase.modeling.datasources import DataSource, DataSourceType
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger


class DatasourceController:
    def __init__(self, config: Union[str, Dict, LunarConfig], persistence_layer: Optional[PersistenceLayer] = None):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._persistence_layer = persistence_layer or PersistenceLayer(config=self._config)
        self.__logger = setup_logger("datasource-controller")

    @property
    def config(self):
        return self._config

    @property
    def persistence_layer(self):
        return self._persistence_layer

    async def get_datasource(self, user_id: str, filters: Optional[Dict] = None):
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
            ds_dict = await self._persistence_layer.get_from_storage_as_dict(
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

            datasources.append(ds)
        return datasources

    async def create_datasource(self, user_id: str, datasource: Dict):
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
        await self._persistence_layer.save_to_storage_as_json(
            path=str(datasource_path), data=datasource.model_dump()
        )

        return datasource

    async def update_datasource(self, user_id: str, datasource: Dict):
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

        await self._persistence_layer.save_to_storage_as_json(
            path=str(datasource_path), data=datasource.model_dump()
        )

        return datasource

    async def upload_local_file(self, user_id: str, datasource_id: str, file):
        datasource_root = Path(
            self._persistence_layer.get_user_datasource_root(user_id)
        )
        if not datasource_root.exists():
            raise ValueError(f"Current user has not datasources defined!")

        datasource_path = Path(datasource_root, f"{datasource_id}.json")
        if not datasource_path.exists():
            raise ValueError(f"Datasource {datasource_id} does not exist!")

        ds_dict = await self._persistence_layer.get_from_storage_as_dict(
            path=str(datasource_path)
        )
        try:
            ds = DataSource.polymorphic_validation(ds_dict)
            ds.connection_attributes.file_name = file.filename
        except ValueError as e:
            raise e

        if ds.type != DataSourceType.LOCAL_FILE:
            raise ValueError(f"Datasource {datasource_id} is not a local file datasource!")

        files_root = Path(self._persistence_layer.get_user_file_root(user_id))
        if not files_root.exists():
            files_root.mkdir(parents=True, exist_ok=True)
        _ = await self._persistence_layer.save_file_to_storage(
            path=str(files_root), file=file
        )

        await self._persistence_layer.save_to_storage_as_json(
            path=str(datasource_path), data=ds.model_dump()
        )

        self.__logger.info(f"Uploaded file {file.filename}")
        return ds.id

    async def delete_datasource(self, user_id: str, datasource_id: str):
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

        ds_dict = await self._persistence_layer.get_from_storage_as_dict(
            path=str(ds_path)
        )
        try:
            ds = DataSource.polymorphic_validation(ds_dict)
        except ValueError:
            raise ValueError(f"Invalid datasource for user {user_id} at {str(ds_path)}")

        files_root = Path(self._persistence_layer.get_user_file_root(user_id))
        if ds.type == DataSourceType.LOCAL_FILE:
            _file = ds.to_component_input(base_path=str(files_root))
            if Path(_file.path).exists():
                await self._persistence_layer.delete(str(_file.path))

        await self._persistence_layer.delete(path=str(datasource_path))

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