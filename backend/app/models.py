import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class InstrumentType(str, enum.Enum):
    FX = "fx"; INDEX = "index"; EQUITY = "equity"; FUND = "fund"


class AlarmKind(str, enum.Enum):
    BELOW = "below"; ABOVE = "above"; PERCENT_DROP = "percent_drop"


class Instrument(Base):
    __tablename__ = "instruments"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[InstrumentType] = mapped_column(Enum(InstrumentType))
    currency: Mapped[str] = mapped_column(String(8))


class Quote(Base):
    __tablename__ = "quotes"
    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.id"), index=True)
    provider: Mapped[str] = mapped_column(String(40)); series_id: Mapped[str] = mapped_column(String(80))
    quote_type: Mapped[str] = mapped_column(String(30)); value: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    bid: Mapped[Decimal | None] = mapped_column(Numeric(20, 8)); ask: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    currency: Mapped[str] = mapped_column(String(8)); unit: Mapped[str] = mapped_column(String(20))
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True)); delay_seconds: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(30)); valuation_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AllowedUser(Base):
    __tablename__ = "allowed_users"
    uid: Mapped[str] = mapped_column(String(128), primary_key=True); email: Mapped[str | None] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Watchlist(Base):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("user_id", "instrument_id"),)
    id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[str] = mapped_column(index=True)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.id")); target_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))


class Alarm(Base):
    __tablename__ = "alarms"
    id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[str] = mapped_column(index=True)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.id")); kind: Mapped[AlarmKind] = mapped_column(Enum(AlarmKind))
    threshold: Mapped[Decimal] = mapped_column(Numeric(20, 8)); percent: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    reference_value: Mapped[Decimal] = mapped_column(Numeric(20, 8)); reference_source: Mapped[str] = mapped_column(String(30))
    reference_at: Mapped[datetime] = mapped_column(DateTime(timezone=True)); active: Mapped[bool] = mapped_column(Boolean, default=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(100)); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NotificationEvent(Base):
    __tablename__ = "notification_events"
    __table_args__ = (UniqueConstraint("alarm_id", "quote_id", name="uq_alarm_quote"),)
    id: Mapped[int] = mapped_column(primary_key=True); alarm_id: Mapped[int] = mapped_column(ForeignKey("alarms.id"))
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id")); user_id: Mapped[str] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending"); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[str] = mapped_column(index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True); active: Mapped[bool] = mapped_column(Boolean, default=True)

