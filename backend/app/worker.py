import asyncio

import httpx
from sqlalchemy import desc, select

from .config import get_settings
from .database import SessionLocal
from .models import Alarm, DeviceToken, NotificationEvent, Quote
from .providers import get_provider
from .services import evaluate_alarm


async def run_once(step:int=0):
    settings=get_settings();provider=get_provider(settings.data_provider)
    with SessionLocal() as db:
        for q in provider.quotes(step):
            delay=max(0,int((q.received_at-q.as_of).total_seconds())); row=Quote(**q.__dict__,delay_seconds=delay);db.add(row)
        db.commit()
        for alarm in db.scalars(select(Alarm).where(Alarm.active.is_(True)).with_for_update(skip_locked=True)).all():
            quote=db.scalar(select(Quote).where(Quote.instrument_id==alarm.instrument_id).order_by(desc(Quote.as_of)).limit(1))
            if quote:evaluate_alarm(db,alarm,quote)
        events=db.scalars(select(NotificationEvent).where(NotificationEvent.status=="pending")).all()
        async with httpx.AsyncClient(timeout=10) as client:
            for event in events:
                tokens=db.scalars(select(DeviceToken).where(DeviceToken.user_id==event.user_id,DeviceToken.active.is_(True))).all()
                if not tokens:event.status="no_device";continue
                try:
                    response=await client.post(settings.expo_push_url,json=[{"to":t.token,"title":"Fiyat alarmı tetiklendi","body":"Belirlediğiniz eşik sağlandı.","data":{"alarmId":event.alarm_id}} for t in tokens]);response.raise_for_status();event.status="ticket_accepted"
                except httpx.HTTPError:event.status="retry"
        db.commit()


async def main():
    step=0
    while True:
        await run_once(step);step+=1;await asyncio.sleep(get_settings().worker_interval_seconds)


if __name__=="__main__":asyncio.run(main())

