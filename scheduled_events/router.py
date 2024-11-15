from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy import orm
from config.database import get_db, SessionLocal
from .models import ScheduledEvent
from typing import  List
from .schema import ScheduledEventCreate, ScheduledEventResponse
from datetime import datetime
import schedule, time as datetime_time, requests, threading
from collections import deque



router = APIRouter()

def daily_task():
    global newEvent
    print("TASK BOOTS UP")
    today = datetime.now().date()
    current_time = datetime.now().time()
    db: orm.Session = SessionLocal()

    try:
        events_today = db.query(ScheduledEvent).filter(ScheduledEvent.date == today , ScheduledEvent.time > current_time).order_by(ScheduledEvent.time).all()
        # print("Events Today: ", events_today)
        if events_today:
            events_stack = list(events_today)

            events_queue = deque(events_today)

            print(f" {len(events_queue)} Events scheduled for today: ")
            
            while events_queue:
                event = events_queue.popleft()

                print(f"Processing event '{event.type}' scheduled at {event.time}")
                now = datetime.now()

                event_time = datetime.combine(now.date(), event.time)
                

                # Calculate the time difference between now and event_time
                time_diff = event_time - now

                print("Time diff: ", time_diff)

                try:
                    body = event.value

                    headers = {
                        'x-tenant-id': 'ai'
                    }

                    time_to_wait = time_diff.total_seconds()
                    print(f"Waiting for {time_to_wait} seconds before sending the request...")

                    if time_to_wait < 0:
                        continue
                    sleep_time = int(time_to_wait)
                    interval = 5

                    for _ in range(0, sleep_time, interval):
                        # print("new loop")
                        if newEvent:
                            print("Rerunning daily_task")
                            newEvent = False
                            return daily_task()
                        
                        datetime_time.sleep(interval)  # Delay execution for `time_to_wait` seconds


                    response = requests.post('https://whatsappbotserver.azurewebsites.net/send-template', json=body,headers=headers)
                    # Check if the request was successful
                    if response.status_code == 200:
                        print(f"Event '{event.type}' processed successfully.")
                    else:
                        print(f"Failed to process event '{event.type}'. Status code: {response.status_code}")

                except requests.Timeout:
                    print(f"Request timed out for event '{event.type}'.")

                except requests.RequestException as e:
                    print(f"Request failed for event '{event.type}': {e}")

        else:
            print("No events scheduled for today.")

    finally:
        db.close()

schedule.every().day.at("00:00:00").do(daily_task)

def run_scheduler():
    while True:
        schedule.run_pending()
        datetime_time.sleep(60) 

        # daily_task()

@router.on_event("startup")
def startup_event():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

@router.get("/")
def read_root():
    return {"message": "FastAPI server with scheduled task is running"}


@router.post("/scheduled-events/", response_model=ScheduledEventResponse)
def create_scheduled_event(event: ScheduledEventCreate, db: orm.Session = Depends(get_db)):
    global newEvent
    db_event = ScheduledEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    # background_tasks.add_task(daily_task)
    newEvent = True
    return db_event

@router.get("/scheduled-events/{event_id}", response_model=ScheduledEventResponse)
def get_scheduled_event(event_id: int, db: orm.Session = Depends(get_db)):
    db_event = db.query(ScheduledEvent).filter(ScheduledEvent.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Scheduled event not found")
    return db_event

@router.get("/scheduled-events/", response_model=List[ScheduledEventResponse])
def list_scheduled_events(db: orm.Session = Depends(get_db)):
    events = db.query(ScheduledEvent).all()
    return events

@router.delete("/scheduled-events/{event_id}", status_code=204)
def delete_scheduled_event(event_id: int, db: orm.Session = Depends(get_db)):
    db_event = db.query(ScheduledEvent).filter(ScheduledEvent.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Scheduled event not found")
    db.delete(db_event)
    db.commit()
