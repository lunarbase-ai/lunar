#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Any, Dict, Type, cast, Union, Callable
from lunarbase.ioc.service_token import ServiceToken, T
from dataclasses import dataclass


@dataclass
class LazyRegistration:
    is_factory: bool
    implementation: Union[Type[T], Callable[[], T]]
    deps: Dict[str, Any]

class LunarContainer:
    def __init__(self):
        self._instances: Dict[Type, Any] = {} 
        self._lazy: Dict[Type, LazyRegistration] = {}
        self._name_to_token: Dict[str, ServiceToken] = {}
    
    def register(self, token: ServiceToken[T], cls: Type[T], name: str = None, **deps) -> None:
        if self._has_service(token):
            raise ValueError(f"Service of type {token.service_type.__name__} is already registered")
            
        if name and name in self._name_to_token:
            raise ValueError(f"Service with name '{name}' is already registered")
            
        self._lazy[token.service_type] = LazyRegistration(
            is_factory=False,
            implementation=cls,
            deps=deps
        )
        if name:
            self._name_to_token[name] = token
    
    def register_factory(self, token: ServiceToken[T], factory: Callable[[], T], name: str = None, **deps) -> None:
        if not callable(factory):
            raise ValueError("Factory must be callable")
        if self._has_service(token):
            raise ValueError(f"Factory or service for type {token.service_type.__name__} is already registered")

        if name and name in self._name_to_token:
            raise ValueError(f"Service with name '{name}' is already registered")
            
        self._lazy[token.service_type] = LazyRegistration(
            is_factory=True,
            implementation=factory,
            deps=deps
        )
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
            registration = self._lazy[service_type]
            resolved_deps = self._resolve_dependencies(registration.deps)
            instance = registration.implementation(**resolved_deps)
            
            self._instances[service_type] = instance
            return cast(T, instance)
        
        raise KeyError(f"Service of type {service_type.__name__} not found")

    def reset(self) -> None:
        self._instances.clear()
        self._lazy.clear()
        self._name_to_token.clear()

    def _resolve_dependencies(self, deps: Dict[str, Any]) -> Dict[str, Any]:
        resolved_deps = {}
        for key, value in deps.items():
            if isinstance(value, ServiceToken):
                resolved_deps[key] = self.get(value)
            else:
                resolved_deps[key] = value
        return resolved_deps
        
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