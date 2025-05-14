#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from typing import Protocol
from lunarbase.ioc.container import LunarContainer, LazyRegistration
from lunarbase.ioc.tokens import ServiceToken


class TestService(Protocol):
    def get_value(self) -> str:
        ...

class TestImplementation:
    def __init__(self, value: str = "test"):
        self._value = value
    
    def get_value(self) -> str:
        return self._value

class AnotherService(Protocol):
    def get_name(self) -> str:
        ...

class AnotherImplementation:
    def __init__(self, name: str = "another"):
        self._name = name
    
    def get_name(self) -> str:
        return self._name

@pytest.fixture
def container():
    return LunarContainer()

@pytest.fixture
def test_token():
    return ServiceToken[TestService](TestService)

@pytest.fixture
def another_token():
    return ServiceToken[AnotherService](AnotherService)

@pytest.fixture
def config_token():
    return ServiceToken[ConfigService](ConfigService)

@pytest.fixture
def dependent_token():
    return ServiceToken[DependentService](DependentService)

def test_register_service(container, test_token):
    container.register(test_token, TestImplementation)
    service = container.get(test_token)
    assert isinstance(service, TestImplementation)
    assert service.get_value() == "test"

def test_register_service_with_name(container, test_token):
    container.register(test_token, TestImplementation, name="test_service")
    service = container.test_service
    assert isinstance(service, TestImplementation)
    assert service.get_value() == "test"

def test_register_duplicate_service(container, test_token):
    container.register(test_token, TestImplementation)
    with pytest.raises(ValueError, match="Service of type TestService is already registered"):
        container.register(test_token, TestImplementation)

def test_register_duplicate_name(container, test_token, another_token):
    container.register(test_token, TestImplementation, name="test_service")
    with pytest.raises(ValueError, match="Service with name 'test_service' is already registered"):
        container.register(another_token, AnotherImplementation, name="test_service")

def test_register_factory(container, test_token):
    def create_service():
        return TestImplementation("factory_created")
    
    container.register_factory(test_token, create_service)
    service = container.get(test_token)
    assert isinstance(service, TestImplementation)
    assert service.get_value() == "factory_created"

def test_register_factory_with_name(container, test_token):
    def create_service():
        return TestImplementation("factory_created")
    
    container.register_factory(test_token, create_service, name="test_service")
    service = container.test_service
    assert isinstance(service, TestImplementation)
    assert service.get_value() == "factory_created"

def test_register_duplicate_factory(container, test_token):
    def create_service1():
        return TestImplementation("first")
    
    def create_service2():
        return TestImplementation("second")
    
    container.register_factory(test_token, create_service1)
    with pytest.raises(ValueError, match="Factory or service for type TestService is already registered"):
        container.register_factory(test_token, create_service2)

def test_get_nonexistent_service(container, test_token):
    with pytest.raises(KeyError, match="Service of type TestService not found"):
        container.get(test_token)

def test_get_nonexistent_attribute(container):
    with pytest.raises(AttributeError, match="No service found for attribute 'nonexistent'"):
        _ = container.nonexistent

def test_factory_caches_instance(container, test_token):
    def create_service():
        return TestImplementation("factory_created")
    
    container.register_factory(test_token, create_service)
    service1 = container.get(test_token)
    service2 = container.get(test_token)
    assert service1 is service2

def test_reset_clears_all_registrations(container, test_token, another_token):
    container.register(test_token, TestImplementation)
    
    def create_service():
        return AnotherImplementation()
    container.register_factory(another_token, create_service, name="another_service")
    
    assert container.get(test_token).get_value() == "test"
    assert container.get(another_token).get_name() == "another"
    assert container.another_service.get_name() == "another"
    
    container.reset()
    
    with pytest.raises(KeyError):
        container.get(test_token)
    with pytest.raises(KeyError):
        container.get(another_token)
    with pytest.raises(AttributeError):
        _ = container.another_service

def test_context_manager_cleans_up(container, test_token):
    with LunarContainer() as ctx_container:
        ctx_container.register(test_token, TestImplementation)
        assert isinstance(ctx_container.get(test_token), TestImplementation)
    
    with pytest.raises(KeyError):
        ctx_container.get(test_token)

def test_context_manager_nested_containers(test_token):
    with LunarContainer() as outer:
        outer.register(test_token, TestImplementation)
        
        with LunarContainer() as inner:
            inner.register(test_token, TestImplementation)
            
            assert inner.get(test_token).get_value() == "test"
            assert outer.get(test_token).get_value() == "test"
        
        with pytest.raises(KeyError):
            inner.get(test_token)
        
        assert outer.get(test_token).get_value() == "test"
    
    with pytest.raises(KeyError):
        outer.get(test_token)

def test_context_manager_preserves_exceptions(test_token):
    with pytest.raises(ValueError, match="test exception"):
        with LunarContainer() as container:
            container.register(test_token, TestImplementation)
            raise ValueError("test exception")
    
    with pytest.raises(KeyError):
        container.get(test_token)

class ConfigService(Protocol):
    def get_value(self, key: str) -> str:
        ...

class ConfigImplementation:
    def __init__(self):
        self._config = {
            "api_key": "test_key",
            "endpoint": "test_endpoint"
        }
    
    def get_value(self, key: str) -> str:
        return self._config[key]

class DependentService(Protocol):
    def get_config_value(self, key: str) -> str:
        ...

class DependentImplementation:
    def __init__(self, config: ConfigService):
        self._config = config
    
    def get_config_value(self, key: str) -> str:
        return self._config.get_value(key)


def test_register_with_dependency(container, config_token, dependent_token):
    container.register(config_token, ConfigImplementation)
    
    container.register(dependent_token, DependentImplementation, config=config_token)
    
    service = container.get(dependent_token)
    
    assert isinstance(service, DependentImplementation)
    assert service.get_config_value("api_key") == "test_key"
    assert service.get_config_value("endpoint") == "test_endpoint"

def test_register_factory_with_dependency(container, config_token, dependent_token):
    container.register(config_token, ConfigImplementation)
    
    def create_service(config: ConfigService):
        return DependentImplementation(config)
    
    container.register_factory(dependent_token, create_service, config=config_token)
    
    service = container.get(dependent_token)
    
    assert isinstance(service, DependentImplementation)
    assert service.get_config_value("api_key") == "test_key"

def test_dependency_resolution_order(container, config_token, dependent_token):
    container.register(dependent_token, DependentImplementation, config=config_token)
    
    container.register(config_token, ConfigImplementation)
    
    service = container.get(dependent_token)
    
    assert isinstance(service, DependentImplementation)
    assert service.get_config_value("api_key") == "test_key"

def test_missing_dependency(container, dependent_token):
    container.register(dependent_token, DependentImplementation, config=ServiceToken[ConfigService](ConfigService))
    
    with pytest.raises(KeyError, match="Service of type ConfigService not found"):
        container.get(dependent_token)

def test_circular_dependency(container):
    class ServiceA(Protocol):
        def get_b(self) -> 'ServiceB':
            ...
    
    class ServiceB(Protocol):
        def get_a(self) -> ServiceA:
            ...
    
    class ImplementationA:
        def __init__(self, b: ServiceB):
            self._b = b
        
        def get_b(self) -> ServiceB:
            return self._b
    
    class ImplementationB:
        def __init__(self, a: ServiceA):
            self._a = a
        
        def get_a(self) -> ServiceA:
            return self._a
    
    token_a = ServiceToken[ServiceA](ServiceA)
    token_b = ServiceToken[ServiceB](ServiceB)
    
    container.register(token_a, ImplementationA, b=token_b)
    container.register(token_b, ImplementationB, a=token_a)
    
    with pytest.raises(RecursionError):
        container.get(token_a)

def test_multiple_dependencies(container):
    class ServiceA(Protocol):
        def get_value(self) -> str:
            ...
    
    class ServiceB(Protocol):
        def get_value(self) -> str:
            ...
    
    class ServiceC(Protocol):
        def get_values(self) -> tuple[str, str]:
            ...
    
    class ImplementationA:
        def __init__(self):
            self._value = "A"
        
        def get_value(self) -> str:
            return self._value
    
    class ImplementationB:
        def __init__(self):
            self._value = "B"
        
        def get_value(self) -> str:
            return self._value
    
    class ImplementationC:
        def __init__(self, a: ServiceA, b: ServiceB):
            self._a = a
            self._b = b
        
        def get_values(self) -> tuple[str, str]:
            return (self._a.get_value(), self._b.get_value())
    
    token_a = ServiceToken[ServiceA](ServiceA)
    token_b = ServiceToken[ServiceB](ServiceB)
    token_c = ServiceToken[ServiceC](ServiceC)
    
    container.register(token_a, ImplementationA)
    container.register(token_b, ImplementationB)
    container.register(token_c, ImplementationC, a=token_a, b=token_b)
    
    service_c = container.get(token_c)
    assert service_c.get_values() == ("A", "B")