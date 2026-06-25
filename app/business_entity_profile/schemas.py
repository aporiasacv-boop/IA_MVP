from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class MonthlyBucket(BaseModel):
    movements: int
    amount: Decimal
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")


class JournalSummary(BaseModel):
    distinct_count: int = 0
    top: list[dict] = Field(default_factory=list)


class RelatedAccountItem(BaseModel):
    code: str
    name: str
    movements: int
    amount: Decimal


class RelatedCounterpartyItem(BaseModel):
    code: str
    name: str
    dimension: str
    movements: int
    amount: Decimal


class EntityProfileItem(BaseModel):
    profile_id: int
    canonical_id: int
    canonical_name: str
    primary_rfc: str | None = None
    total_movements: int
    total_amount: Decimal
    average_amount: Decimal
    first_seen: date | None = None
    last_seen: date | None = None
    active_months: int
    active_days: int
    debit_amount: Decimal
    credit_amount: Decimal
    debit_credit_ratio: Decimal | None = None
    related_accounts_count: int
    related_counterparties_count: int
    monthly_distribution: dict[str, MonthlyBucket | dict] = Field(default_factory=dict)
    currencies: list[str] = Field(default_factory=list)
    journals: JournalSummary | dict = Field(default_factory=dict)
    dimensions_used: list[str] = Field(default_factory=list)
    top_accounts: list[RelatedAccountItem | dict] = Field(default_factory=list)
    top_counterparties: list[RelatedCounterpartyItem | dict] = Field(default_factory=list)
    profile_completeness: Decimal
    generated_at: datetime
    updated_at: datetime


class EntityProfileListResponse(BaseModel):
    items: list[EntityProfileItem]
    total: int
    page: int
    page_size: int


class EntityProfileStatisticsResponse(BaseModel):
    entity_profiles_total: int
    canonical_entities_total: int
    profiles_without_movements: int
    average_profile_completeness: float
    profile_generation_time: float
    last_profile_refresh: datetime | None = None
    total_movements_profiled: int
    average_movements_per_profile: float


class ProfileGenerationResult(BaseModel):
    profiles_upserted: int
    profiles_created: int
    profiles_updated: int
    generation_time_seconds: float
