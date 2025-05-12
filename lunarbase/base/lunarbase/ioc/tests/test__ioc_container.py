import pytest
from typing import Protocol
from lunarbase.ioc.container import LunarContainer
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

def test_register_service(container, test_token):
    service = TestImplementation()
    container.register(test_token, service)
    assert container.get(test_token) == service
    assert container.get(test_token).get_value() == "test"

def test_register_service_with_name(container, test_token):
    service = TestImplementation()
    container.register(test_token, service, name="test_service")
    assert container.test_service == service
    assert container.test_service.get_value() == "test"

def test_register_duplicate_service(container, test_token):
    service1 = TestImplementation()
    service2 = TestImplementation()
    container.register(test_token, service1)
    with pytest.raises(ValueError, match="Service of type TestService is already registered"):
        container.register(test_token, service2)

def test_register_duplicate_name(container, test_token, another_token):
    service1 = TestImplementation()
    service2 = AnotherImplementation()
    container.register(test_token, service1, name="test_service")
    with pytest.raises(ValueError, match="Service with name 'test_service' is already registered"):
        container.register(another_token, service2, name="test_service")

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
    service = TestImplementation()
    container.register(test_token, service)
    
    def create_service():
        return AnotherImplementation()
    container.register_factory(another_token, create_service, name="another_service")
    
    assert container.get(test_token) == service
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
        service = TestImplementation()
        ctx_container.register(test_token, service)
        assert ctx_container.get(test_token) == service
    
    with pytest.raises(KeyError):
        ctx_container.get(test_token)

def test_context_manager_nested_containers(test_token):
    with LunarContainer() as outer:
        outer_service = TestImplementation("outer")
        outer.register(test_token, outer_service)
        
        with LunarContainer() as inner:
            inner_service = TestImplementation("inner")
            inner.register(test_token, inner_service)
            
            assert inner.get(test_token).get_value() == "inner"
            
            assert outer.get(test_token).get_value() == "outer"
        
        with pytest.raises(KeyError):
            inner.get(test_token)
        
        assert outer.get(test_token).get_value() == "outer"
    
    with pytest.raises(KeyError):
        outer.get(test_token)

def test_context_manager_preserves_exceptions(test_token):
    with pytest.raises(ValueError, match="test exception"):
        with LunarContainer() as container:
            service = TestImplementation()
            container.register(test_token, service)
            raise ValueError("test exception")
    
    with pytest.raises(KeyError):
        container.get(test_token)
