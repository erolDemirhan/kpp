from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .models import AlarmKind, InstrumentType


class InstrumentOut(BaseModel):
    id: str; symbol: str; name: str; type: InstrumentType; currency: str
    model_config = {"from_attributes": True}


class QuoteOut(BaseModel):
    instrument_id: str; provider: str; quote_type: str; value: Decimal; bid: Decimal | None; ask: Decimal | None
    currency: str; unit: str; as_of: datetime; received_at: datetime; delay_seconds: int; status: str
    valuation_date: datetime | None = None
    model_config = {"from_attributes": True}


class AlarmCreate(BaseModel):
    instrument_id: str; kind: AlarmKind; threshold: Decimal | None = Field(default=None, gt=0)
    percent: Decimal | None = Field(default=None, gt=0, le=100)
    reference_value: Decimal = Field(gt=0); reference_source: str; reference_at: datetime
    trigger_immediately: bool = False


class TargetUpdate(BaseModel):
    target_price: Decimal | None = Field(default=None, gt=0)


class DeviceCreate(BaseModel): token: str = Field(pattern=r"^ExponentPushToken\[.+\]$")

