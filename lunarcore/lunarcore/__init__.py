# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import os.path
from pathlib import Path

from lunarcore.config import LunarConfig
from lunarcore.core.persistence_layer import PersistenceLayer
from lunarcore.errors import ConfigFileIsMissing
from lunarcore.utils import get_config

ENV = f"{Path(__file__).parent.parent.parent.as_posix()}/.env"
GLOBAL_CONFIG = None
if os.path.isfile(ENV):
    GLOBAL_CONFIG = get_config(settings_file_path=ENV)
if GLOBAL_CONFIG is None:
    raise ConfigFileIsMissing(ENV)
