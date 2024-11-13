from pathlib import Path

from lunarbase.config import GLOBAL_CONFIG
from lunarbase.registry import LunarRegistry

REGISTRY = LunarRegistry(
    registry_root=str(Path(__file__).parent), config=GLOBAL_CONFIG
)