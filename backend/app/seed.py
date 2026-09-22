from datetime import UTC, datetime, timedelta

from .database import Base, SessionLocal, engine
from .models import AllowedUser, Instrument, InstrumentType, Quote
from .providers import DemoProvider

INSTRUMENTS=[("usdtry","USD/TRY","ABD Doları / Türk Lirası",InstrumentType.FX,"TRY"),("eurtry","EUR/TRY","Euro / Türk Lirası",InstrumentType.FX,"TRY"),("xu030","XU030","BIST 30",InstrumentType.INDEX,"POINT"),("xu100","XU100","BIST 100",InstrumentType.INDEX,"POINT"),("thyao","THYAO","Türk Hava Yolları",InstrumentType.EQUITY,"TRY"),("akb","AKB","Ak Portföy Birinci Borçlanma Araçları Fonu",InstrumentType.FUND,"TRY")]


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.get(AllowedUser,"demo-user"): db.add(AllowedUser(uid="demo-user",email="demo@example.test"))
        for row in INSTRUMENTS:
            if not db.get(Instrument,row[0]): db.add(Instrument(id=row[0],symbol=row[1],name=row[2],type=row[3],currency=row[4]))
        db.commit()
        if db.query(Quote).count()==0:
            provider=DemoProvider()
            for day in range(60,0,-1):
                for q in provider.quotes(day):
                    at=datetime.now(UTC)-timedelta(days=day)
                    db.add(Quote(instrument_id=q.instrument_id,provider=q.provider,series_id=q.series_id,quote_type=q.quote_type,value=q.value,bid=q.bid,ask=q.ask,currency=q.currency,unit=q.unit,as_of=at,received_at=at,delay_seconds=0,status=q.status,valuation_date=q.valuation_date))
            db.commit()


if __name__ == "__main__": seed()

