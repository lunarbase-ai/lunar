from typing import Any, Dict, TypeVar, Generic, Type, cast
from lunarbase.ioc.tokens import ServiceToken, T

class LunarContainer:
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
        self._name_to_token: Dict[str, ServiceToken] = {}
    
    def register(self, token: ServiceToken[T], instance: T, name: str = None) -> None:
        if self._has_service(token):
            raise ValueError(f"Service of type {token.service_type.__name__} is already registered")

        if self._has_named_service(name):
            raise ValueError(f"Service with name '{name}' is already registered")
            
        self._services[token.service_type] = instance
        if name:
            self._name_to_token[name] = token
    
    def register_factory(self, token: ServiceToken[T], factory: callable, name: str = None) -> None:
        if not callable(factory):
            raise ValueError("Factory must be callable")
        if self._has_service(token):
            raise ValueError(f"Factory or service for type {token.service_type.__name__} is already registered")

        if self._has_named_service(name):
            raise ValueError(f"Factory or service with name '{name}' is already registered")
            
        self._factories[token.service_type] = factory
        if name:
            self._name_to_token[name] = token
    
    def get(self, token: ServiceToken[T]) -> T:
        service_type = token.service_type
        
        if service_type in self._services:
            return cast(T, self._services[service_type])
        
        if service_type in self._factories:
            service = self._factories[service_type]()
            self._services[service_type] = service
            return cast(T, service)
        
        raise KeyError(f"Service of type {service_type.__name__} not found")

    def reset(self) -> None:
        self._services.clear()
        self._factories.clear()
        self._name_to_token.clear()

    def _has_service(self, token: ServiceToken[T]) -> bool:
        return token.service_type in self._services or token.service_type in self._factories

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