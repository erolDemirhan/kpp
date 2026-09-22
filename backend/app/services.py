from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from math import exp, sqrt
from statistics import mean, pstdev

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import Alarm, AlarmKind, NotificationEvent, Quote


def calculate_threshold(reference: Decimal, percent: Decimal) -> Decimal:
    return reference * (Decimal("1") - percent / Decimal("100"))


def quote_is_valid(quote: Quote, last_as_of: datetime | None = None) -> bool:
    now = datetime.now(UTC); as_of = quote.as_of.replace(tzinfo=UTC) if quote.as_of.tzinfo is None else quote.as_of
    return quote.value > 0 and quote.status not in {"invalid", "outage"} and (now-as_of).total_seconds() <= get_settings().quote_max_age_seconds and (last_as_of is None or quote.as_of >= last_as_of)


def alarm_matches(alarm: Alarm, value: Decimal) -> bool:
    return value <= alarm.threshold if alarm.kind in {AlarmKind.BELOW, AlarmKind.PERCENT_DROP} else value >= alarm.threshold


def evaluate_alarm(db: Session, alarm: Alarm, quote: Quote) -> NotificationEvent | None:
    if not alarm.active or alarm.blocked_reason or not quote_is_valid(quote) or not alarm_matches(alarm, quote.value): return None
    event = NotificationEvent(alarm_id=alarm.id, quote_id=quote.id, user_id=alarm.user_id, status="pending", created_at=datetime.now(UTC))
    db.add(event); alarm.active = False
    try: db.commit()
    except IntegrityError: db.rollback(); return None
    db.refresh(event); return event


def next_business_day(start: date, steps: int) -> date:
    value = start
    for _ in range(steps):
        value += timedelta(days=1)
        while value.weekday() >= 5: value += timedelta(days=1)
    return value


def forecast(values: list[Decimal], horizon: int, cutoff: datetime) -> dict:
    if len(values) < 30: return {"available": False, "reason": "En az 30 geçerli gözlem gerekli."}
    prices = [float(v) for v in values]; returns = [math_log(prices[i]/prices[i-1]) for i in range(1, len(prices))]
    window = returns[-20:]; drift = mean(window); vol = pstdev(window); center = prices[-1] * exp(drift*horizon)
    spread = 1.28155 * vol * sqrt(horizon)
    return {"available": True, "horizon": horizon, "target_date": next_business_day(cutoff.date(), horizon).isoformat(),
            "p10": str(Decimal(str(center*exp(-spread))).quantize(Decimal("0.0001"))), "p50": str(Decimal(str(center)).quantize(Decimal("0.0001"))),
            "p90": str(Decimal(str(center*exp(spread))).quantize(Decimal("0.0001"))), "baseline": str(values[-1]), "model_version": "logtrend-vol-v1",
            "cutoff": cutoff.isoformat(), "observations": len(values), "indicators": {"20_step_log_trend": drift, "20_step_volatility": vol},
            "disclaimer": "Tahminler belirsizlik içerir; yatırım tavsiyesi değildir."}


def math_log(value: float) -> float:
    from math import log
    return log(value)


def walk_forward(values: list[Decimal], horizon: int, minimum: int = 30) -> dict:
    errors=[]; baseline=[]; covered=0
    for end in range(minimum, len(values)-horizon+1):
        prediction=forecast(values[:end], horizon, datetime(2025,1,1,tzinfo=UTC)); actual=float(values[end+horizon-1])
        center=float(prediction["p50"]); errors.append(abs(center-actual)); baseline.append(abs(float(values[end-1])-actual))
        covered += float(prediction["p10"]) <= actual <= float(prediction["p90"])
    return {"samples":len(errors), "mae": mean(errors) if errors else None, "baseline_mae":mean(baseline) if baseline else None, "band_coverage":covered/len(errors) if errors else None}

