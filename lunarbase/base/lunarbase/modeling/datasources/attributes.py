import mimetypes
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator, model_serializer


class LocalFileConnectionAttributes(BaseModel):
    file_name: str = Field(default=...)
    file_type: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def validate_local_file(self):
        if self.file_type is None:
            self.file_type, _ = mimetypes.guess_type(self.file_name)
            if self.file_type is None:
                raise ValueError(
                    f"Could not determine file type for {self.file_name}! Please specify file_type!"
                    f"Accepted values are {mimetypes.types_map.values()}"
                )
        return self


class PostgresqlConnectionAttributes(BaseModel):
    url: Optional[str] = Field(default=None)
    driver_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    host: Optional[str] = Field(default=None)
    port: str = Field(default="5432")
    database: Optional[str] = Field(default=None)
    additional_connection_kwargs: Optional[Dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_connection_attributes(self):
        if self.url is not None:
            _url = urlparse(self.url)
            if _url.scheme != "sqlite":
                left_url, _, right_url = self.url.rpartition("@")
                self.driver_name, credentials = left_url.split("://", 1)
                self.username, self.password = credentials.split(":", 1)
                host, self.database = right_url.split("/", 1)
                self.host, _, self.port = host.rpartition(":")
            else:
                self.driver_name = _url.scheme
                self.database = _url.path

        else:
            if self.driver_name is None:
                raise ValueError(
                    "Driver name must be specified when url is not provided!"
                )
            if self.host is None:
                raise ValueError("Host must be specified when url is not provided!")
            if self.database is None:
                raise ValueError("Database must be specified when url is not provided!")
        return self


class SparqlConnectionAttributes(BaseModel):
    endpoint: str = Field(default=..., description="SPARQL endpoint's URI")
    updateEndpoint: Optional[str] = Field(default=None, description="SPARQL endpoint's URI for SPARQL Update operations (if it's a different one)")
    user: Optional[str] = Field(default=None, description="The username of the credentials for querying the current endpoint")
    passwd: Optional[str] = Field(default=None, description="The password of the credentials for querying the current endpoint")
    http_auth: str = Field(default="BASIC", description="HTTP Authentication type. The default value is BASIC. Possible values are BASIC or DIGEST. It is used only in case the credentials are set.")
    timeout: int = Field(default=30, description="The timeout (in seconds) to use for querying the endpoint.")
