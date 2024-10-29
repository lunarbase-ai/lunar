# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Components are downloaded from <https://github.com/lunarbase-labs/lunarverse>.
Please add any new components to the repository above.
"""
import os

from lunarbase.lunarbase.config import GLOBAL_CONFIG

from lunarbase.lunarbase.registry import ComponentRegistry


COMPONENT_REGISTRY = ComponentRegistry(
    registry_root=os.path.join(os.path.dirname(__file__)), config=GLOBAL_CONFIG
)
