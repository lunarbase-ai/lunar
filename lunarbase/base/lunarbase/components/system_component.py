from lunarcore.component.lunar_component import LunarComponent
from typing import Dict, Any
from lunarbase.ioc.container import LunarContainer
from abc import abstractmethod, ABC
from lunarcore.component.data_types import DataType
from lunarcore.component.component_group import ComponentGroup

class SystemComponent(
    LunarComponent,
    component_name="SystemComponent",
    component_description="Base class for system components that require dependency injection",
    input_types={},
    output_type=DataType.ANY,
    component_group=ComponentGroup.LUNAR
):
    @abstractmethod
    def resolve_deps(self, container: LunarContainer) -> Dict[str, Any]:
        pass
    
    @classmethod
    def create(cls, container: LunarContainer, **kwargs):
        temp = cls(deps={}, **kwargs)
        return cls(deps=temp.resolve_deps(container), **kwargs)
    
    def __init__(self, deps: Dict[str, Any], **kwargs):
        super().__init__(configuration=kwargs)
        self.deps = deps