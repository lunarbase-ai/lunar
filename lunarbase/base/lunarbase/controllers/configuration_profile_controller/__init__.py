from pathlib import Path
from typing import Union, Dict, Optional

from lunarbase import LunarConfig
from lunarbase.modeling.configuration_profiles import ConfigurationProfile
from lunarbase.modeling.configuration_profiles.typings import ConfigurationProfileType
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger


class ConfigurationProfileController:
    def __init__(
        self,
        config: Union[str, Dict, LunarConfig],
        persistence_layer: Optional[PersistenceLayer] = None,
    ):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.model_validate(config)
        self._persistence_layer = persistence_layer or PersistenceLayer(
            config=self._config
        )
        self.__logger = setup_logger("configuration-profile-controller")

    @property
    def config(self):
        return self._config

    @property
    def persistence_layer(self):
        return self._persistence_layer

    def get_configuration_profile(self, user_id: str, filters: Optional[Dict] = None):
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

        configuration_profile_root = Path(
            self._persistence_layer.get_configuration_profile_root(user_id)
        )
        if not configuration_profile_root.exists():
            return

        config_profiles = []
        for cp in configuration_profile_root.glob("*.json"):
            cp_dict = self._persistence_layer.get_from_storage_as_dict(path=str(cp))
            if filters is not None:
                accept = fltr(cp_dict, filters)
                if not accept:
                    continue
            try:
                cp = ConfigurationProfile.model_validate(cp_dict)
            except ValueError as e:
                self.__logger.warning(f"Invalid configuration profile: {e}")
                continue
            if cp is not None:
                config_profiles.append(cp)
        return config_profiles

    def create_configuration_profile(self, user_id: str, configuration_profile: Dict):
        try:
            config_profile = ConfigurationProfile.model_validate(configuration_profile)
        except ValueError as e:
            raise ValueError(f"Invalid configuration profile: {str(e)}")

        configuration_profile_root = Path(
            self._persistence_layer.get_configuration_profile_root(user_id)
        )
        if not configuration_profile_root.exists():
            configuration_profile_root.mkdir(parents=True, exist_ok=True)

        config_profile_path = Path(
            configuration_profile_root, f"{config_profile.id}.json"
        )
        self._persistence_layer.save_to_storage_as_json(
            path=str(config_profile_path), data=config_profile.model_dump()
        )

        return config_profile

    def update_configuration_profile(self, user_id: str, configuration_profile: Dict):
        try:
            config_profile = ConfigurationProfile.model_validate(configuration_profile)
        except ValueError as e:
            raise ValueError(f"Invalid configuration profile: {str(e)}")

        configuration_profile_root = Path(
            self._persistence_layer.get_configuration_profile_root(user_id)
        )
        if not configuration_profile_root.exists():
            raise ValueError("Current user has not configuration profiles defined!")

        config_profile_path = Path(
            configuration_profile_root, f"{config_profile.id}.json"
        )
        if not config_profile_path.exists():
            raise ValueError("Noting to update: configuration profile does not exist!")
        self._persistence_layer.save_to_storage_as_json(
            path=str(config_profile_path), data=config_profile.model_dump()
        )

        return config_profile

    def delete_configuration_profile(self, user_id: str, configuration_profile_id: str):
        configuration_profile_root = Path(
            self._persistence_layer.get_configuration_profile_root(user_id)
        )
        if not configuration_profile_root.exists():
            raise ValueError("Current user has not configuration profiles defined!")

        config_profile_path = Path(
            configuration_profile_root, f"{configuration_profile_id}.json"
        )
        if not config_profile_path.exists():
            raise ValueError("Noting to delete: configuration profile does not exist!")

        self._persistence_layer.delete(path=str(config_profile_path))

        return True

    @staticmethod
    def get_configuration_profile_types():
        configuration_profiles = []
        for e in ConfigurationProfileType:
            configuration_profiles.append(
                {
                    "id": e.name,
                    "name": e.name.replace("_", " "),
                }
            )
        return configuration_profiles
