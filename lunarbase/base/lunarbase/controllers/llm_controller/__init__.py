from pathlib import Path
from typing import Union, Dict, Optional

from lunarbase import LunarConfig
from lunarbase.modeling.llms import LLM, LLMType
from lunarbase.persistence import PersistenceLayer
from lunarbase.utils import setup_logger


class LLMController:
    def __init__(
        self,
        config: Union[str, Dict, LunarConfig],
        persistence_layer: Optional[PersistenceLayer] = None,
    ):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._persistence_layer = persistence_layer or PersistenceLayer(
            config=self._config
        )
        self.__logger = setup_logger("llm-controller")

    def get_llm(self, user_id: str, filters: Optional[Dict] = None):
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

        llm_root = Path(self._persistence_layer.get_user_llm_root(user_id))
        if not llm_root.exists():
            return

        llms = []
        for llm in llm_root.glob("*.json"):
            llm_dict = self._persistence_layer.get_from_storage_as_dict(
                path=str(llm)
            )
            if filters is not None:
                accept = fltr(llm_dict, filters)
                if not accept:
                    continue
            try:
                llm = LLM.polymorphic_validation(llm_dict)
            except ValueError:
                continue

            llms.append(llm)
        return llms

    def create_llm(self, user_id: str, llm: Dict):
        try:
            llm = LLM.polymorphic_validation(llm)
        except ValueError as e:
            raise ValueError(f"Invalid llm: {str(e)}")

        llm_root = Path(self._persistence_layer.get_user_llm_root(user_id))
        if not llm_root.exists():
            llm_root.mkdir(parents=True, exist_ok=True)

        llm_path = Path(llm_root, f"{llm.id}.json")
        self._persistence_layer.save_to_storage_as_json(
            path=str(llm_path), data=llm.model_dump()
        )

        return llm

    def update_llm(self, user_id: str, llm: Dict):
        try:
            llm = LLM.polymorphic_validation(llm)
        except ValueError as e:
            raise ValueError(f"Invalid llm: {str(e)}")

        llm_root = Path(self._persistence_layer.get_user_llm_root(user_id))
        if not llm_root.exists():
            raise ValueError(f"Current user has not llms defined!")

        llm_path = Path(llm_root, f"{llm.id}.json")
        if not llm_path.exists():
            raise ValueError(f"LLM {llm.id} does not exist!")

        self._persistence_layer.save_to_storage_as_json(
            path=str(llm_path), data=llm.model_dump()
        )

        return llm

    def delete_llm(self, user_id: str, llm_id: str):
        llm_root = Path(self._persistence_layer.get_user_llm_root(user_id))
        if not llm_root.exists():
            raise ValueError(f"Current user has not llms defined!")

        llm_path = Path(llm_root, f"{llm_id}.json")
        if not llm_path.exists():
            raise ValueError(f"LLM {llm_id} does not exist!")

        self._persistence_layer.delete(path=str(llm_path))

        return True

    @staticmethod
    def get_llm_types(self):
        llms = []
        for e in LLMType:
            llms.append(
                {
                    "id": e.name,
                    "name": e.name.replace("_", " "),
                    "connectionAttributes": e.expected_connection_attributes()[1]

                }
            )
        return llms
