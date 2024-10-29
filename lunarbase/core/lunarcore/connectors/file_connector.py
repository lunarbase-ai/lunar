# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import glob
import os
from pathlib import Path
from typing import AnyStr, Generator, Union, Optional

from lunarbase import File


class FileConnector:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = None
        if base_dir is not None:
            self.connect(base_dir)

    def connect(self, base_dir: str):
        """
        Must be called before use
        """
        self.base_dir = os.path.abspath(base_dir)
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)

    def create_directory(self, directory_name):
        if self.base_dir is None:
            raise FileNotFoundError(
                f"FileConnector must be initialized with a base path!"
            )
        dir_path = os.path.join(self.base_dir, directory_name)
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise e
        return dir_path

    def create_file(
        self, file_name: str, content: Union[AnyStr, Generator[AnyStr, None, None]]
    ):
        """
        Every file location will be treated relative to the base_path
        """

        if self.base_dir is None:
            raise FileNotFoundError(
                f"FileConnector must be initialized with a base path!"
            )

        file_path = os.path.join(self.base_dir, file_name)
        if os.path.exists(file_path):
            raise FileExistsError(f"File '{file_name}' already exists.")

        try:
            with open(file_path, "w") as file:
                if isinstance(content, str):
                    file.write(content)
                elif hasattr(content, "__iter__"):
                    for chunk in content:
                        file.write(chunk)
                else:
                    raise TypeError(
                        "Content must be a string or an iterable of strings"
                    )
        except Exception as e:
            raise e

    def read_file(self, file_name: str, chunk_size: int = -1):
        """
        Every file location will be treated relative to the base_path
        """

        if self.base_dir is None:
            raise FileNotFoundError(
                f"FileConnector must be initialized with a base path!"
            )

        file_path = os.path.join(self.base_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")

        try:
            with open(file_path, "r") as file:
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break
                    yield data
        except Exception as e:
            raise e

    def list_all_files(self):
        if self.base_dir is None:
            raise FileNotFoundError(
                f"FileConnector must be initialized with a base path!"
            )

        file_list = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_type = os.path.splitext(file_path)[1]
                if len(file_type) == 0:
                    continue
                file_size = os.path.getsize(file_path)
                file_list.append(
                    File(
                        name=file,
                        type=file_type,
                        path=file_path,
                        size=file_size,
                    )
                )
        return file_list

    def delete_file(self, file_name: str):
        if self.base_dir is None:
            raise FileNotFoundError(
                f"FileConnector must be initialized with a base path!"
            )

        file_path = os.path.join(self.base_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_name}' not found.")
        if not os.path.isfile(file_path):
            raise IsADirectoryError(f"'{file_name}' is not a file.")

        try:
            os.remove(file_path)
        except Exception as e:
            raise e

    def get_absolute_path(self, relative_path: str):
        if self.base_dir is None:
            raise FileNotFoundError(
                f"FileConnector must be initialized with a base path!"
            )

        candidate_paths = glob.glob(os.path.join(self.base_dir, relative_path))
        if len(candidate_paths) > 0:
            return str(candidate_paths[0])

        return None
