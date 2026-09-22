from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.models import Alarm, AlarmKind, Quote
from app.services import alarm_matches, calculate_threshold, evaluate_alarm, quote_is_valid


def make_alarm(kind=AlarmKind.PERCENT_DROP, threshold=Decimal("95")):
    return Alarm(user_id="demo-user",instrument_id="thyao",kind=kind,threshold=threshold,percent=5,reference_value=100,reference_source="current_quote",reference_at=datetime.now(UTC),active=True,created_at=datetime.now(UTC))
def test_decimal_percent_threshold_and_equality():
    assert calculate_threshold(Decimal("100"),Decimal("5")) == Decimal("95")
    assert calculate_threshold(Decimal("100"),Decimal("10")) == Decimal("90")
    assert alarm_matches(make_alarm(),Decimal("95")); assert alarm_matches(make_alarm(AlarmKind.ABOVE),Decimal("95"))
def test_stale_invalid_and_out_of_order_quote():
    q=Quote(instrument_id="thyao",provider="demo",series_id="s",quote_type="last_trade",value=1,currency="TRY",unit="para",as_of=datetime.now(UTC)-timedelta(hours=2),received_at=datetime.now(UTC),delay_seconds=1,status="fresh")
    assert not quote_is_valid(q); q.as_of=datetime.now(UTC); q.status="invalid"; assert not quote_is_valid(q)
    q.status="fresh"; assert not quote_is_valid(q,datetime.now(UTC)+timedelta(seconds=1))
def test_event_is_idempotent_across_restart(db):
    alarm=make_alarm(); db.add(alarm); db.commit(); q=db.query(Quote).filter_by(instrument_id="thyao").order_by(Quote.as_of.desc()).first(); q.as_of=datetime.now(UTC); q.value=Decimal("90"); db.commit()
    assert evaluate_alarm(db,alarm,q) is not None
    alarm.active=True; db.commit(); assert evaluate_alarm(db,alarm,q) is None
