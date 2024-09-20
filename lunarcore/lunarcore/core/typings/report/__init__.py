# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from uuid import uuid4

from pydantic import BaseModel, Field


class ReportSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow: str = Field(...)
    name: str = Field(...)
    content: str = Field(...)
