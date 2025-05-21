#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest

class TestGlob:
    def test_find_files(self, connection, sample_files):
        results = connection.glob(sample_files, pattern="*/*.txt")
        result_names = sorted([p.name for p in results])
        assert result_names == ["file1.txt", "file2.txt", "file3.txt"]

    def test_find_no_files(self, connection, tmp_path):
        results = connection.glob(tmp_path, pattern="*.doesnotexist")
        assert results == [] 