import os

from lunarbase.config import GLOBAL_CONFIG
from lunarbase.registry import LunarRegistry

REGISTRY = LunarRegistry(
    registry_root=os.path.join(os.path.dirname(__file__)), config=GLOBAL_CONFIG
)