#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import zipfile
from pathlib import Path

class TestExtractZip:
    def test_extracts_zip_to_default_location(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            zip_ref.writestr("file1.txt", "content1")
            zip_ref.writestr("subdir/file2.txt", "content2")
        
        extracted_files = connection.extract_zip(str(zip_path))
        
        extract_dir = tmp_path / "test"
        assert extract_dir.exists()
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "subdir" / "file2.txt").exists()
        assert len(extracted_files) == 2
        assert any("file1.txt" in f for f in extracted_files)
        assert any("file2.txt" in f for f in extracted_files)

    def test_extracts_zip_to_specified_location(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            zip_ref.writestr("file1.txt", "content1")
        
        extract_to = tmp_path / "custom_dir"
        extracted_files = connection.extract_zip(str(zip_path), str(extract_to))
        
        assert extract_to.exists()
        assert (extract_to / "file1.txt").exists()
        assert len(extracted_files) == 1
        assert any("file1.txt" in f for f in extracted_files)

    def test_raises_error_for_nonexistent_zip(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        nonexistent_zip = tmp_path / "nonexistent.zip"
        
        with pytest.raises(FileNotFoundError):
            connection.extract_zip(str(nonexistent_zip))

    def test_raises_error_for_invalid_zip(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)
        
        invalid_zip = tmp_path / "invalid.zip"
        invalid_zip.write_bytes(b"not a zip file")
        
        with pytest.raises(zipfile.BadZipFile):
            connection.extract_zip(str(invalid_zip))

    def test_raises_error_for_corrupted_zip(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)

        zip_path = tmp_path / "corrupted.zip"
        with open(zip_path, 'wb') as f:
            f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')
        
        with pytest.raises(zipfile.BadZipFile):
            connection.extract_zip(str(zip_path))

    def test_raises_error_for_invalid_extract_path(self, connection, tmp_path):
        connection._lunar_base_path = str(tmp_path)

        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            zip_ref.writestr("file1.txt", "content1")

        invalid_path = "/should_not_exist"
        with pytest.raises(ValueError):
            connection.extract_zip(str(zip_path), invalid_path) 