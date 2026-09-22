from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .auth import User, current_user
from .database import get_db
from .models import Alarm, DeviceToken, Instrument, NotificationEvent, Quote, Watchlist
from .schemas import AlarmCreate, DeviceCreate, InstrumentOut, QuoteOut, TargetUpdate
from .services import calculate_threshold, forecast

app=FastAPI(title="Piyasa Takip API",version="0.1.0",description="DEMO sentetik piyasa verisi API'si")
app.add_middleware(CORSMiddleware,allow_origins=[],allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["Authorization","Content-Type","X-Demo-User"])

@app.get("/health")
def health(): return {"status":"ok","mode":"DEMO — sentetik veri"}

@app.get("/instruments",response_model=list[InstrumentOut])
def instruments(q: str="",db:Session=Depends(get_db),_:User=Depends(current_user)):
    stmt=select(Instrument)
    if q: stmt=stmt.where(Instrument.name.ilike(f"%{q}%") | Instrument.symbol.ilike(f"%{q}%"))
    return db.scalars(stmt.limit(50)).all()

def latest_quote(db:Session,instrument_id:str):
    return db.scalar(select(Quote).where(Quote.instrument_id==instrument_id).order_by(desc(Quote.as_of)).limit(1))

@app.get("/instruments/{instrument_id}/quote",response_model=QuoteOut)
def quote(instrument_id:str,db:Session=Depends(get_db),_:User=Depends(current_user)):
    value=latest_quote(db,instrument_id)
    if not value: raise HTTPException(404,"Fiyat bulunamadı")
    return value

@app.get("/instruments/{instrument_id}/history")
def history(instrument_id:str,limit:int=Query(60,ge=2,le=365),db:Session=Depends(get_db),_:User=Depends(current_user)):
    rows=db.scalars(select(Quote).where(Quote.instrument_id==instrument_id).order_by(desc(Quote.as_of)).limit(limit)).all()
    return [{"value":str(x.value),"asOf":x.as_of,"seriesId":x.series_id} for x in reversed(rows)]

@app.get("/instruments/{instrument_id}/forecast")
def get_forecast(instrument_id:str,db:Session=Depends(get_db),_:User=Depends(current_user)):
    rows=list(reversed(db.scalars(select(Quote).where(Quote.instrument_id==instrument_id).order_by(desc(Quote.as_of)).limit(120)).all()))
    if not rows: raise HTTPException(404,"Veri bulunamadı")
    return {"oneDay":forecast([r.value for r in rows],1,rows[-1].as_of),"oneWeek":forecast([r.value for r in rows],5,rows[-1].as_of),"explanation":{"summary":"Son 20 gözlemdeki logaritmik trend ve oynaklık kullanıldı.","indicators":["20 adımlık log trend","20 adımlık oynaklık"],"uncertainties":["Geçmiş hareketler geleceği garanti etmez","Haber ve makro veri kullanılmadı"],"sourceIds":[rows[-1].series_id]}}

@app.get("/watchlist")
def watchlist(db:Session=Depends(get_db),user:User=Depends(current_user)):
    rows=db.execute(select(Watchlist,Instrument).join(Instrument).where(Watchlist.user_id==user.uid)).all()
    return [{"id":w.id,"instrument":InstrumentOut.model_validate(i),"targetPrice":w.target_price,"quote":latest_quote(db,i.id)} for w,i in rows]

@app.post("/watchlist/{instrument_id}",status_code=201)
def add_watch(instrument_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if not db.get(Instrument,instrument_id): raise HTTPException(404,"Varlık bulunamadı")
    old=db.scalar(select(Watchlist).where(Watchlist.user_id==user.uid,Watchlist.instrument_id==instrument_id))
    if old:return old
    value=Watchlist(user_id=user.uid,instrument_id=instrument_id);db.add(value);db.commit();db.refresh(value);return value

@app.delete("/watchlist/{instrument_id}",status_code=204)
def remove_watch(instrument_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    row=db.scalar(select(Watchlist).where(Watchlist.user_id==user.uid,Watchlist.instrument_id==instrument_id))
    if row:db.delete(row);db.commit()
    return Response(status_code=204)

@app.patch("/watchlist/{instrument_id}/target")
def target(instrument_id:str,payload:TargetUpdate,db:Session=Depends(get_db),user:User=Depends(current_user)):
    row=db.scalar(select(Watchlist).where(Watchlist.user_id==user.uid,Watchlist.instrument_id==instrument_id))
    if not row:raise HTTPException(404,"Takip kaydı bulunamadı")
    row.target_price=payload.target_price;db.commit();return {"targetPrice":row.target_price}

@app.post("/alarms",status_code=201)
def create_alarm(payload:AlarmCreate,db:Session=Depends(get_db),user:User=Depends(current_user)):
    threshold=calculate_threshold(payload.reference_value,payload.percent) if payload.kind.value=="percent_drop" and payload.percent else payload.threshold
    if threshold is None:raise HTTPException(422,"Eşik veya yüzde gerekli")
    current=latest_quote(db,payload.instrument_id); already=current and ((payload.kind.value in {"below","percent_drop"} and current.value<=threshold) or (payload.kind.value=="above" and current.value>=threshold))
    if already and not payload.trigger_immediately:raise HTTPException(409,"Eşik şu anda sağlanıyor; hemen bildirim için onay gerekli")
    row=Alarm(user_id=user.uid,instrument_id=payload.instrument_id,kind=payload.kind,threshold=threshold,percent=payload.percent,reference_value=payload.reference_value,reference_source=payload.reference_source,reference_at=payload.reference_at,active=True,created_at=datetime.now(UTC));db.add(row);db.commit();db.refresh(row);return row

@app.get("/alarms")
def alarms(db:Session=Depends(get_db),user:User=Depends(current_user)):return db.scalars(select(Alarm).where(Alarm.user_id==user.uid)).all()

@app.get("/notifications")
def notifications(db:Session=Depends(get_db),user:User=Depends(current_user)):return db.scalars(select(NotificationEvent).where(NotificationEvent.user_id==user.uid).order_by(desc(NotificationEvent.created_at))).all()

@app.post("/devices",status_code=201)
def device(payload:DeviceCreate,db:Session=Depends(get_db),user:User=Depends(current_user)):
    row=db.scalar(select(DeviceToken).where(DeviceToken.token==payload.token)) or DeviceToken(token=payload.token,user_id=user.uid,active=True);row.user_id=user.uid;row.active=True;db.add(row);db.commit();return {"registered":True}

@app.delete("/devices/{token}",status_code=204)
def delete_device(token:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    row=db.scalar(select(DeviceToken).where(DeviceToken.token==token,DeviceToken.user_id==user.uid))
    if row:row.active=False;db.commit()
    return Response(status_code=204)

