from datetime import UTC, datetime
from decimal import Decimal

from app.services import forecast, next_business_day, walk_forward


def test_market_weekend_calendar(): assert next_business_day(datetime(2025,1,3).date(),1).isoformat()=='2025-01-06'
def test_forecast_and_walk_forward_do_not_use_future():
    values=[Decimal(100+i) for i in range(60)]; a=forecast(values[:40],5,datetime.now(UTC)); b=forecast(values[:40]+[Decimal('99999')],5,datetime.now(UTC))
    assert a['observations']==40 and a['p50']!=b['p50']; assert walk_forward(values,5)['samples']==26
def test_numeric_forecast_survives_without_llm(): assert forecast([Decimal(i) for i in range(1,40)],1,datetime.now(UTC))['available']
