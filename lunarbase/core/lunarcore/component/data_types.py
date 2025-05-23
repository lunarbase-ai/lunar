# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase
import types
from enum import Enum
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

Embedding = List[Union[float, int]]


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class EmbeddedText(BaseModel):
    text: str
    embeddings: Embedding
    metadata: Optional[Any] = None

class RawBinaryFileContent(BaseModel):
    type: Literal["raw_binary"] = "raw_binary"
    content: bytes

class RawTextFileContent(BaseModel):
    type: Literal["raw_text"] = "raw_text"
    content: str

class Base64FileContent(BaseModel):
    type: Literal["base64"] = "base64"
    content: str

class File(BaseModel):
    path: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    size: Optional[int] = None
    preview: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Union[RawBinaryFileContent, RawTextFileContent, Base64FileContent]] = Field(default=None, discriminator="type")


class Select(BaseModel):
    """
    Not used yet!
    """

    options: List[str] = Field(default_factory=list, frozen=True)
    selection: str = Field(default=...)

    class Config:
        populate_by_name = True
        validate_assignment = True

    @field_validator("selection")
    @classmethod
    def validate_selection(cls, value, info: ValidationInfo):
        _options = info.data.get("options", [])
        if value not in _options:
            raise ValueError(
                f"{value} not a valid option! Valid options are: {_options}!"
            )
        return value


class DataType(Enum):
    FILE = "FILE"
    DATASOURCE = "DATASOURCE"
    TEXT = "TEXT"
    CSV = "CSV"
    INT = "INT"
    FLOAT = "FLOAT"
    CODE = "CODE"
    R_CODE = "R_CODE"
    EMBEDDINGS = "EMBEDDINGS"
    JSON = "JSON"
    IMAGE = "IMAGE"
    REPORT = "REPORT"
    TEMPLATE = "TEMPLATE"
    LIST = "LIST"
    AGGREGATED = "AGGREGATED"
    PROPERTY_SELECTOR = "PROPERTY_SELECTOR"
    PROPERTY_GETTER = "PROPERTY_GETTER"
    LIST_INDEX_GETTER = "LIST_INDEX_GETTER"
    WORKFLOW = "WORKFLOW"
    BSGN_GRAPH = "BSGN_GRAPH"
    CYTOSCAPE = "CYTOSCAPE"
    PASSWORD = "PASSWORD"
    BAR_CHART = "BAR_CHART"
    LINE_CHART = "LINE_CHART"
    AUDIO = "AUDIO"
    BOOL = "BOOL"
    STREAM = "STREAM"
    SPARQL = "SPARQL"
    SELECT = "SELECT"
    ANY = "ANY"
    NULL = "NULL"

    def type(self):
        if self == DataType.FILE:
            return File
        elif self == DataType.DATASOURCE:
            return str
        elif self == DataType.SELECT:
            return Select
        elif self == DataType.TEXT:
            return str
        elif self == DataType.INT:
            return int
        elif self == DataType.FLOAT:
            return float
        elif self in [DataType.CODE, DataType.R_CODE]:
            return str
        elif self == DataType.EMBEDDINGS:
            return list
        elif self == DataType.JSON:
            return dict
        elif self == DataType.IMAGE:
            return str
        elif self == DataType.REPORT:
            return str
        elif self == DataType.TEMPLATE:
            return str
        elif self == DataType.LIST:
            return list
        elif self == DataType.AGGREGATED:
            return dict
        elif self == DataType.PROPERTY_SELECTOR:
            return str
        elif self == DataType.PROPERTY_GETTER:
            return str
        elif self == DataType.LIST_INDEX_GETTER:
            return str
        elif self == DataType.WORKFLOW:
            return Union[str, dict]
        elif self == DataType.BSGN_GRAPH:
            return dict
        elif self == DataType.CYTOSCAPE:
            return dict
        elif self == DataType.PASSWORD:
            return str
        elif self == DataType.CSV:
            return str
        elif self == DataType.BAR_CHART:
            return dict
        elif self == DataType.LINE_CHART:
            return dict
        elif self == DataType.AUDIO:
            return str
        elif self == DataType.BOOL:
            return bool
        elif self == DataType.STREAM:
            return types.GeneratorType
        elif self == DataType.SPARQL:
            return str
        elif self == DataType.ANY:
            return any
        elif self == DataType.NULL:
            return type(None)

        return None

    def __repr__(self):
        if self == DataType.BOOL:
            return str(str2bool(self.value))

        return str(self.value)

    def __str__(self):
        return self.__repr__()
