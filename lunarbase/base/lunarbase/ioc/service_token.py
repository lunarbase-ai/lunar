#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import TypeVar, Generic, Type

T = TypeVar('T')

class ServiceToken(Generic[T]):
    def __init__(self, service_type: Type[T]):
        self.service_type = service_type