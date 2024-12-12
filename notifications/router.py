from fastapi import APIRouter, Request, Depends, HTTPException, Header
from sqlalchemy import orm
from config.database import get_db
from .models import Notifications
from typing import Optional
from datetime import datetime, timedelta
router = APIRouter()

@router.post("/notifications")
async def add_notifications(req: Request, db: orm.Session = Depends(get_db)):
    tenant_id = req.headers.get('X-Tenant-Id')
    body = await req.json()  # Use await to extract the JSON body asynchronously
    content = body.get('content')

    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID is required in the headers.")
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is required in the request body.")

    notification = Notifications(
        content=content,
        tenant_id=tenant_id
    )

    try:
        db.add(notification)
        db.commit()
        db.refresh(notification)  # Refresh to get the updated notification object with any DB-generated fields (like id)
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail="Failed to add notification.")
    
    return {"message": "Notification added successfully", "notification_id": notification.id}

@router.get("/notifications")
def get_notifications(
    day: Optional[int] = None, #no of days in past
    x_tenant_id: Optional[str] = Header(None), 
    db: orm.Session = Depends(get_db)
):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID is required in the headers.")
    
    if day:
        today = datetime.now()
        that_day = today - timedelta(days=day)
        notifications = db.query(Notifications).filter(Notifications.tenant_id == x_tenant_id).filter(Notifications.created_on == that_day)
    else:
        notifications = db.query(Notifications).filter(Notifications.tenant_id == x_tenant_id).all()

    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for the tenant.")

    return {"notifications": notifications}


@router.get("/notifications/{page_no}")
def get_limited_notifications(
    page_no: int,
    x_tenant_id: Optional[str] = Header(None),
    db: orm.Session = Depends(get_db),
):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID is required in the headers.")
    
    limit = 10  # Number of contacts per page
    offset = limit * (page_no - 1)
    
    total = db.query(Notifications).filter(Notifications.tenant_id == x_tenant_id).count()

    total_pages = (total + limit - 1) // limit  # Round up

    notifications = (
            db.query(Notifications)
            .filter(Notifications.tenant_id == x_tenant_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    return {
        "contacts": notifications,
        "page_no": page_no or None,
        "page_size": limit or None,
        "total_contacts": len(notifications),
        "total_pages": total_pages or None,
    }

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    db: orm.Session = Depends(get_db)
):
    notification = db.query(Notifications).filter(Notifications.id == notification_id).first()

    db.delete(notification)
    db.commit()
    
    return True