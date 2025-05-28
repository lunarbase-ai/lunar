#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import io
from pathlib import Path
from fastapi import UploadFile

class TestSaveFile:
    def test_save_file_creates_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_content = b"hello lunarbase"
        file_name = "testfile.txt"
        upload_file = UploadFile(filename=file_name, file=io.BytesIO(file_content))
        
        connection.save_file("files", upload_file)
        expected_file = tmp_path / "files" / file_name
        assert expected_file.exists()
        assert expected_file.read_bytes() == file_content

    def test_save_file_overwrites_existing_file(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_name = "overwrite.txt"
        file_dir = tmp_path / "files"
        file_dir.mkdir(parents=True, exist_ok=True)
        file_path = file_dir / file_name
        file_path.write_bytes(b"old content")
        new_content = b"new content"
        upload_file = UploadFile(filename=file_name, file=io.BytesIO(new_content))
       
        connection.save_file("files", upload_file)
        assert file_path.exists()
        assert file_path.read_bytes() == new_content

    def test_save_file_invalid_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        file_content = b"should fail"
        file_name = "fail.txt"

        invalid_path = "/should_not_exist"
        upload_file = UploadFile(filename=file_name, file=io.BytesIO(file_content))
        with pytest.raises(ValueError, match="Problem encountered with path"):
            connection.save_file(invalid_path, upload_file) 