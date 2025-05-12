from typing import Any, Dict, TypeVar, Generic, Type, cast, Union, Callable, TypedDict
from lunarbase.ioc.tokens import ServiceToken, T


class LazyRegistration(TypedDict):
    implementation: Union[Type[T], Callable[[], T]]
    kwargs: dict
    is_factory: bool

class LunarContainer:
    def __init__(self):
        self._instances: Dict[Type, Any] = {} 
        self._lazy: Dict[Type, LazyRegistration] = {}
        self._name_to_token: Dict[str, ServiceToken] = {}
    
    def register(self, token: ServiceToken[T], cls: Type[T], name: str = None, **kwargs) -> None:
        if self._has_service(token):
            raise ValueError(f"Service of type {token.service_type.__name__} is already registered")
            
        if name and name in self._name_to_token:
            raise ValueError(f"Service with name '{name}' is already registered")
            
        self._lazy[token.service_type] = (cls, kwargs, False)
        if name:
            self._name_to_token[name] = token
    
    def register_factory(self, token: ServiceToken[T], factory: Callable[[], T], name: str = None) -> None:
        if not callable(factory):
            raise ValueError("Factory must be callable")
        if self._has_service(token):
            raise ValueError(f"Factory or service for type {token.service_type.__name__} is already registered")

        if name and name in self._name_to_token:
            raise ValueError(f"Service with name '{name}' is already registered")
            
        self._lazy[token.service_type] = (factory, {}, True)
        if name:
            self._name_to_token[name] = token
    
    def register_instance(self, token: ServiceToken[T], instance: T, name: str = None) -> None:
        if self._has_service(token):
            raise ValueError(f"Service of type {token.service_type.__name__} is already registered")

        if name and name in self._name_to_token:
            raise ValueError(f"Service with name '{name}' is already registered")
            
        self._instances[token.service_type] = instance
        if name:
            self._name_to_token[name] = token
    
    def get(self, token: ServiceToken[T]) -> T:
        service_type = token.service_type
        
        if service_type in self._instances:
            return cast(T, self._instances[service_type])
        
        if service_type in self._lazy:
            cls_or_factory, kwargs, is_factory = self._lazy[service_type]
            
            if is_factory:
                instance = cls_or_factory()
            else:
                resolved_kwargs = {}
                for key, value in kwargs.items():
                    if isinstance(value, ServiceToken):
                        resolved_kwargs[key] = self.get(value)
                    else:
                        resolved_kwargs[key] = value
                instance = cls_or_factory(**resolved_kwargs)
            
            self._instances[service_type] = instance
            return cast(T, instance)
        
        raise KeyError(f"Service of type {service_type.__name__} not found")

    def reset(self) -> None:
        self._instances.clear()
        self._lazy.clear()
        self._name_to_token.clear()

    def _has_service(self, token: ServiceToken[T]) -> bool:
        return token.service_type in self._instances or token.service_type in self._lazy

    def _has_named_service(self, name: str) -> bool:
        return name in self._name_to_token
    
    def __getattr__(self, name: str) -> Any:
        if self._has_named_service(name):
            token = self._name_to_token[name]
            return self.get(token)
        
        raise AttributeError(f"No service found for attribute '{name}'")

    def __enter__(self) -> 'LunarContainer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.reset()