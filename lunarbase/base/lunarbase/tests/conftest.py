#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest

@pytest.fixture(autouse=True, scope="session")
def setup_integration_test_environment(lunar_context):
    lunar_context.lunar_registry.load_cached_components()
    lunar_context.lunar_registry.register()