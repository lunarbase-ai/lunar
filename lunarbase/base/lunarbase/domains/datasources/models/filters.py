from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from lunarbase.modeling.datasources import DataSourceType

class DataSourceFilters(BaseModel):
    """Filter fields that can be used to filter datasources in the index method."""

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

    class Config:
        extra = "forbid"