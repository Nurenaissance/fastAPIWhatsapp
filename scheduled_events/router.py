from fastapi import APIRouter, Depends ,HTTPException, Header
from sqlalchemy import orm
from config.database import get_db, SessionLocal
from .models import ScheduledEvent
from typing import  List, Optional
from .schema import ScheduledEventCreate, ScheduledEventResponse
from datetime import datetime
import schedule, time as datetime_time, requests, threading
from collections import deque



router = APIRouter()

restart_event = threading.Event()

def daily_task():
    print("TASK BOOTS UP")
    today = datetime.now().date()
    current_time = datetime.now().time()
    db: orm.Session = SessionLocal()

    try:
        events_today = db.query(ScheduledEvent).filter(
            ScheduledEvent.date == today, ScheduledEvent.time > current_time
        ).order_by(ScheduledEvent.time).all()

        if events_today:
            events_queue = deque(events_today)
            print(f"{len(events_queue)} Events scheduled for today:")

            while events_queue:
                event = events_queue.popleft()
                print(f"Processing event '{event.type}' scheduled at {event.time}")
                now = datetime.now()
                event_time = datetime.combine(now.date(), event.time)
                time_diff = event_time - now
                print("Time diff:", time_diff)

                time_to_wait = time_diff.total_seconds()
                if time_to_wait < 0:
                    continue

                sleep_time = int(time_to_wait)
                interval = 5  # Check every 5 seconds

                for _ in range(0, sleep_time, interval):
                    if restart_event.is_set():
                        print("Restarting daily_task due to new event...")
                        restart_event.clear()
                        return daily_task()

                    # print("Waiting...")
                    datetime_time.sleep(interval)

                # Make the request
                try:
                    body = event.value
                    # headers = {'x-tenant-id': 'ai'}
                    response = requests.post(
                        'https://whatsappbotserver.azurewebsites.net/send-template',
                        json=body
                    )
                    if response.status_code == 200:
                        print(f"Event '{event.type}' processed successfully.")
                    else:
                        print(f"Failed to process event '{event.type}'. Status code: {response.status_code}")

                except requests.RequestException as e:
                    print(f"Request failed for event '{event.type}': {e}")
        else:
            print("No events scheduled for today.")

    finally:
        db.close()

schedule.every().day.at("00:00:00").do(daily_task)

def run_scheduler():
    while True:
        # print("running scheduler")
        schedule.run_pending()
        # print("Sleeping for 10 seconds")
        if restart_event.is_set():
            print("Restarting daily_task in run scheduler")
            restart_event.clear()
            daily_task()
        # print("sleeping..")
        datetime_time.sleep(5)

        # daily_task()

@router.on_event("startup")
def startup_event():
    print(schedule.get_jobs())
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    restart_event.set()


@router.get("/")
def read_root():
    return {"message": "FastAPI server with scheduled task is running"}


@router.post("/scheduled-events/", response_model=ScheduledEventResponse)
def create_scheduled_event(event: ScheduledEventCreate, x_tenant_id: Optional[str] = Header(None) ,db: orm.Session = Depends(get_db)):
    global newEvent
        
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID is required in the headers.")

    db_event = ScheduledEvent(**event.dict(), tenant_id = x_tenant_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    restart_event.set()

    return db_event

@router.get("/scheduled-events/{event_id}/", response_model=ScheduledEventResponse)
def get_scheduled_event(event_id: int, db: orm.Session = Depends(get_db)):
    db_event = db.query(ScheduledEvent).filter(ScheduledEvent.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Scheduled event not found")
    return db_event

@router.get("/scheduled-events/", response_model=List[ScheduledEventResponse])
def list_scheduled_events(x_tenant_id : Optional[str] = Header(None), db: orm.Session = Depends(get_db)):
    events = db.query(ScheduledEvent).filter(ScheduledEvent.tenant_id == x_tenant_id).all()
    return events

@router.delete("/scheduled-events/{event_id}/", status_code=204)
def delete_scheduled_event(event_id: int, db: orm.Session = Depends(get_db)):
    db_event = db.query(ScheduledEvent).filter(ScheduledEvent.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Scheduled event not found")
    db.delete(db_event)
    db.commit()

    restart_event.set()
