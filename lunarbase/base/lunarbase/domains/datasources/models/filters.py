from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from lunarbase.modeling.datasources import DataSourceType

class DataSourceFilters(BaseModel):
    id: Optional[UUID] = Field(
        default=None,
        description="Filter by datasource id"
    )
    
    name: Optional[str] = Field(
        default=None,
        description="Filter by datasource name"
    )
    type: Optional[DataSourceType] = Field(
        default=None,
        description="Filter by datasource type"
    )

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(DataSourceFilters, id_value):
        if id_value is None:
            return id_value
        if isinstance(id_value, UUID):
            return id_value
        if isinstance(id_value, str):
            try:
                return UUID(id_value)
            except ValueError:
                raise ValueError(f"id must be a valid UUID string, got: {id_value}")
        raise ValueError(f"id must be a UUID or valid UUID string, got: {type(id_value)}")

    class Config:
        extra = "forbid"