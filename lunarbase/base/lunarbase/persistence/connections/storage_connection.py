#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from lunarbase.config import LunarConfig

class StorageConnection(ABC):

    def __init__(self, config: LunarConfig):
        self._config = config

    @property
    def config(self) -> LunarConfig:
        return self._config
    
    @abstractmethod
    def connect(self) -> "StorageConnection":
        pass

    @abstractmethod
    def disconnect(self):
        pass