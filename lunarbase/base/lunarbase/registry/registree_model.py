#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import os
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator


class ComponentRegistree(BaseModel):
    name: str = Field(default=...)
    location: str = Field(default=...)
    subdirectory: Optional[str] = Field(default=None)
    github_token: Optional[str] = Field(default=None)
    is_local: bool = Field(default=False)
    branch: str = Field(default="main")

    @model_validator(mode="after")
    def validate_registree(self):
        self.is_local = os.path.exists(self.location)

        parsed_location = urlparse(self.location)
        is_remote = len(parsed_location.scheme) > 0 and not self.is_local
        is_github = is_remote and "github.com" in parsed_location.hostname

        if not self.is_local and not is_github:
            raise ValueError(
                f"Failed to parse component location {self.location}. "
                f"Only local- or Github-based locations are supported."
            )

        if self.is_local and self.subdirectory is not None:
            if not os.path.isdir(os.path.join(self.location, self.subdirectory)):
                raise ValueError(
                    f"Failed to parse component location {self.location}. "
                    f"Subdirectory {self.subdirectory} may not exist."
                )

        if is_github:
            self.is_local = False
            if self.github_token is not None:
                access_location = parsed_location._replace(
                    netloc=f"{self.github_token}@{parsed_location.netloc}"
                )
                self.location = access_location.geturl()
        return self
