#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from pathlib import Path

class TestBuildPath:
    def test_builds_a_path(self, connection):
        params = ["path", "to", "file"]
        path = connection.build_path(*params)
        expected = str(Path(*params))
        assert path == expected 