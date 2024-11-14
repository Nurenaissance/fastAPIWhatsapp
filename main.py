from fastapi import FastAPI, Depends, HTTPException, Request, Header, responses, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from config.database import engine, Base, get_db, SessionLocal
from models import Contact, Tenant, WhatsappTenantData, Product, NodeTemplate, MessageStatus, ScheduledEvent
from schema import ScheduledEventCreate, ScheduledEventResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from config.middleware import add_cors_middleware
from datetime import datetime
import schedule, time as datetime_time, threading, requests
from collections import deque


newEvent = False
app = FastAPI()

add_cors_middleware(app)

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get('/node-templates/')
def read_nodetemps(request: Request, db: Session = Depends(get_db)):
    tenant_id = request.headers.get("X-Tenant-Id")
    if not tenant_id:
        return HTTPException(status_code=400, detail="Tenant ID is missing in headers")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    node_temps = db.query(NodeTemplate).filter(NodeTemplate.tenant_id == tenant_id).all()

    if not node_temps:
        raise HTTPException(status_code=404, detail="No contacts found for this tenant")

    return node_temps


@app.get("/contacts/")
def read_contacts(request: Request, db: Session = Depends(get_db)):
    # Extract tenant_id from request headers
    tenant_id = request.headers.get("X-Tenant-Id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID missing in headers")

    # Verify that the tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    contacts = db.query(Contact).filter(Contact.tenant_id == tenant_id).all()
    
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found for this tenant")

    return contacts



@app.get("/whatsapp_tenant/")
def get_whatsapp_tenant_data(x_tenant_id: Optional[str] = Header(None), bpid: Optional[str] = Header(None), db: Session = Depends(get_db)):
    try:
        # Retrieve WhatsappTenantData for the specified tenant
        print("TENANT AND BPID:", x_tenant_id, bpid)
        whatsapp_data_json = {}

        if x_tenant_id:
            whatsapp_data = db.query(WhatsappTenantData).filter(WhatsappTenantData.tenant_id == x_tenant_id).all()
            if not whatsapp_data:
                raise HTTPException(status_code=404, detail="WhatsappTenantData not found for tenant")
            whatsapp_data_json = whatsapp_data
            tenant_id = x_tenant_id
        elif bpid:
            whatsapp_data = db.query(WhatsappTenantData).filter(WhatsappTenantData.business_phone_number_id == bpid).all()
            if not whatsapp_data:
                raise HTTPException(status_code=404, detail="WhatsappTenantData not found for bpid")
            tenant_id = whatsapp_data[0].tenant_id
            print("Tenant:", tenant_id)
            whatsapp_data_json = whatsapp_data
        else:
            raise HTTPException(status_code=400, detail="Either Tenant-ID or BPID header must be provided")

        catalog_data = db.query(Product).filter(Product.tenant_id == tenant_id).all()
        # print("catalog: ", catalog_data)
        catalog_data_json = catalog_data

        return {"whatsapp_data": whatsapp_data, "catalog_data": catalog_data}
        return responses.JSONResponse(content={"whatsapp_data": whatsapp_data_json, "catalog_data": catalog_data_json})

    except Exception as e:
        print("Error occurred with tenant:", x_tenant_id)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
@app.get("/get-status/")
def get_status(request: Request, db: Session = Depends(get_db)):
    try:
        statuses = db.query(MessageStatus).all()
        
        groupedStatuses = {}
        for status in statuses:
            bg_group = status.broadcast_group
            if bg_group not in groupedStatuses:
                groupedStatuses[bg_group] = {"sent": 0,"delivered": 0,"read": 0,"replied": 0,"failed": 0}
            
            if status.sent:
                groupedStatuses[bg_group]["sent"] += 1
            if status.delivered:
                groupedStatuses[bg_group]["delivered"] += 1
            if status.read:
                groupedStatuses[bg_group]["read"] += 1
            if status.replied:
                groupedStatuses[bg_group]["replied"] += 1
            if status.failed:
                groupedStatuses[bg_group]["failed"] += 1
        


        # distinct_groups = db.execute(select(MessageStatus.broadcast_group).distinct()).scalars().all()

        # for group in distinct_groups:

        #     sent_count = db.query(func.count()).filter(MessageStatus.sent == True, MessageStatus.broadcast_group == group).scalar()
        #     delivered_count = db.query(func.count()).filter(MessageStatus.delivered == True, MessageStatus.broadcast_group == group).scalar()
        #     read_count = db.query(func.count()).filter(MessageStatus.read == True, MessageStatus.broadcast_group == group).scalar()
        #     failed_count = db.query(func.count()).filter(MessageStatus.failed == True, MessageStatus.broadcast_group == group).scalar()
        #     replied_count = db.query(func.count()).filter(MessageStatus.replied == True, MessageStatus.broadcast_group == group).scalar()

        #     groupedStatuses[group] = {"sent": sent_count, "delivered": delivered_count ,"read": read_count, "replied": replied_count, "failed": failed_count}

        
        return groupedStatuses
            
        # statuses = db.query(MessageStatus).all()
        # sent_count = db.query(func.count()).filter(MessageStatus.sent == True).scalar()
        # delivered_count = db.query(func.count()).filter(MessageStatus.delivered == True).scalar()
        # read_count = db.query(func.count()).filter(MessageStatus.read == True).scalar()
        # failed_count = db.query(func.count()).filter(MessageStatus.failed == True).scalar()
        # replied_count = db.query(func.count()).filter(MessageStatus.replied == True).scalar()


        # for status in statuses:
        #     bg_group = status.broadcast_group or "null"
        #     sent = status.sent
        #     delivered = status.delivered
        #     read = status.delivered
        #     replied = status.replied
        #     failed = status.failed
            
        #     if bg_group not in groupedStatuses:
        #         groupedStatuses[bg_group] = []

        #     groupedStatuses[bg_group].append(status)

        # # Combine the counts in a dictionary
        # counts = {
        #     "sent_count": sent_count,
        #     "delivered_count": delivered_count,
        #     "read_count": read_count,
        #     "failed_count": failed_count,
        #     "replied_count": replied_count,
        # }


    except Exception as e:
        # Catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

def daily_task():
    global newEvent
    print("TASK BOOTS UP")
    today = datetime.now().date()
    current_time = datetime.now().time()
    db: Session = SessionLocal()

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

@app.on_event("startup")
def startup_event():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

@app.get("/")
def read_root():
    return {"message": "FastAPI server with scheduled task is running"}


@app.post("/scheduled-events/", response_model=ScheduledEventResponse)
def create_scheduled_event(event: ScheduledEventCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    global newEvent
    db_event = ScheduledEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    # background_tasks.add_task(daily_task)
    newEvent = True
    return db_event



@app.get("/scheduled-events/{event_id}", response_model=ScheduledEventResponse)
def get_scheduled_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(ScheduledEvent).filter(ScheduledEvent.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Scheduled event not found")
    return db_event

@app.get("/scheduled-events/", response_model=List[ScheduledEventResponse])
def list_scheduled_events(db: Session = Depends(get_db)):
    events = db.query(ScheduledEvent).all()
    return events

@app.delete("/scheduled-events/{event_id}", status_code=204)
def delete_scheduled_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(ScheduledEvent).filter(ScheduledEvent.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Scheduled event not found")
    db.delete(db_event)
    db.commit()