import os

from lunarbase.config import GLOBAL_CONFIG
from lunarbase.registry import ComponentRegistry

COMPONENT_REGISTRY = ComponentRegistry(
    registry_root=os.path.join(os.path.dirname(__file__)), config=GLOBAL_CONFIG
)