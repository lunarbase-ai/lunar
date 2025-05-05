from functools import cache
from pathlib import Path
from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry
from pydantic import BaseModel
from lunarbase.persistence import PersistenceLayer
from lunarbase.controllers.workflow_controller import WorkflowController
from lunarbase.controllers.component_controller import ComponentController

@cache
def lunar_context_factory() -> LunarContext:
    lunar_config = None
    if Path(LunarConfig.DEFAULT_ENV).is_file():
        lunar_config = LunarConfig.get_config(
            settings_file_path=LunarConfig.DEFAULT_ENV
        )
    if lunar_config is None:
        raise FileNotFoundError(LunarConfig.DEFAULT_ENV)

    return LunarContext(
        lunar_config=lunar_config,
        lunar_registry=LunarRegistry(config=lunar_config),

        workflow_controller=WorkflowController(config=lunar_config),
        component_controller=ComponentController(config=lunar_config),

        persistence_layer=PersistenceLayer(config=lunar_config),
    )


LUNAR_CONTEXT = lunar_context_factory()


class LunarContext(BaseModel):
    lunar_config: LunarConfig
    lunar_registry: LunarRegistry