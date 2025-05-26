from typing import TypeVar, Generic, Type

T = TypeVar('T')

class ServiceToken(Generic[T]):
    def __init__(self, service_type: Type[T]):
        self.service_type = service_type