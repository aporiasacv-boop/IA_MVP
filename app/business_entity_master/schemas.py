from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BusinessEntityItem(BaseModel):
    entity_id: int
    entity_code: str
    entity_name: str
    source_system: str
    source_table: str
    source_column: str
    movement_count: int
    movement_amount: Decimal
    first_seen: date | None
    last_seen: date | None
    classification_status: str
    confidence: str | None
    created_at: datetime
    updated_at: datetime


class BusinessEntityListResponse(BaseModel):
    items: list[BusinessEntityItem]
    total: int
    page: int
    page_size: int


class BusinessEntityStatisticsResponse(BaseModel):
    business_entities_total: int
    business_entities_loaded: int
    duplicated_entities: int
    last_entity_refresh: datetime | None
    by_source_column: dict[str, int] = Field(default_factory=dict)
    by_classification_status: dict[str, int] = Field(default_factory=dict)


class EntityLoadResult(BaseModel):
    inserted: int
    updated: int
    total_processed: int
    duplicated_entity_codes: int
