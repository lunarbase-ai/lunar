#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from lunarbase.persistence.connections import LocalFilesStorageConnection
from pathlib import Path

@pytest.fixture
def connection(config):
    connector = LocalFilesStorageConnection(config=config).connect()
    yield connector
    connector.disconnect()

@pytest.fixture
def sample_files(tmp_path):
    a_dir = tmp_path / "a"
    b_dir = tmp_path / "b"
    a_dir.mkdir()
    b_dir.mkdir()

    file1 = a_dir / "file1.txt"
    file2 = a_dir / "file2.txt"
    file3 = b_dir / "file3.txt"

    file1.write_text("content1")
    file2.write_text("content2")
    file3.write_text("content3")
    yield tmp_path 