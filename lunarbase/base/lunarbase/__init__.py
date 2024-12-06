from functools import cache
from pathlib import Path
from types import SimpleNamespace

from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry


@cache
def init_lunar_context():
    context = SimpleNamespace()
    if Path(LunarConfig.DEFAULT_ENV).is_file():
        context.lunar_config = LunarConfig.get_config(
            settings_file_path=LunarConfig.DEFAULT_ENV
        )
    if context.lunar_config is None:
        raise FileNotFoundError(LunarConfig.DEFAULT_ENV)

    context.lunar_registry = LunarRegistry(config=context.lunar_config)
    return context


LUNAR_CONTEXT = init_lunar_context()
