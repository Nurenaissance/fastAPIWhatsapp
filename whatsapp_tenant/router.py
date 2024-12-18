from fastapi import APIRouter, Request, Depends ,HTTPException, Header
from sqlalchemy import orm
from config.database import get_db
from .models import WhatsappTenantData, MessageStatus, BroadcastGroups
from product.models import Product
from typing import Optional
from .schema import BroadcastGroupResponse, BroadcastGroupCreate
from .crud import create_broadcast_group, get_broadcast_group, get_all_broadcast_groups
from typing import List, Optional
from contacts.models import Contact
from datetime import timedelta
router = APIRouter()

@router.get("/whatsapp_tenant/")
def get_whatsapp_tenant_data(x_tenant_id: Optional[str] = Header(None), bpid: Optional[str] = Header(None), db: orm.Session = Depends(get_db)):
    try:
        # Retrieve WhatsappTenantData for the specified tenant
        print("TENANT AND BPID:", x_tenant_id, bpid)
        whatsapp_data_json = {}

        if x_tenant_id:
            if x_tenant_id == "demo":
                x_tenant_id = 'ai'
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

    except Exception as e:
        print("Error occurred with tenant:", x_tenant_id)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    


@router.get("/get-status/")
def get_status(request: Request, db: orm.Session = Depends(get_db)):
    try:
        tenant_id = request.headers.get("X-Tenant-Id")
        # whatsapp_data = db.query(WhatsappTenantData).filter(WhatsappTenantData.tenant_id == tenant_id).all()

        statuses = db.query(MessageStatus).filter(MessageStatus.tenant_id == tenant_id)

        groupedStatuses = {}
        for status in statuses:
            bg_group = status.broadcast_group
            template_name = status.template_name

            if bg_group == None:
                key = template_name 
            else:
                key = bg_group

            if key not in groupedStatuses:
                groupedStatuses[key] = { "name": status.broadcast_group_name or None, "sent": 0,"delivered": 0,"read": 0,"replied": 0,"failed": 0, "template_name": template_name}
            
            if status.sent:
                groupedStatuses[key]["sent"] += 1
            if status.delivered:
                groupedStatuses[key]["delivered"] += 1
            if status.read:
                groupedStatuses[key]["read"] += 1
            if status.replied:

                groupedStatuses[key]["replied"] += 1
            if status.failed:
                groupedStatuses[key]["failed"] += 1

        contacts = db.query(Contact).filter(Contact.tenant_id == tenant_id).order_by(Contact.id.asc()).all()
        for contact in contacts:
            
            key = contact.template_key or "Untracked"
            delivered = contact.last_delivered
            replied = contact.last_replied

            if delivered is None or replied is None:
                continue

            if key not in groupedStatuses:
                groupedStatuses[key] = { "name": "Group B", "sent": 0,"delivered": 0,"read": 0,"replied": 0,"failed": 0, "template_name": "Untracked"}
            
            time_diff = contact.last_delivered - contact.last_replied
            if time_diff < timedelta(minutes=1):
                groupedStatuses[key]["replied"] += 1
        
        return groupedStatuses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}",) 

@router.post("/set-status/")
async def set_status(request: Request, db: orm.Session =Depends(get_db)):
    try:
        data = await request.json()

        business_phone_number_id = data.get("business_phone_number_id")
        user_phone_number = data.get("user_phone_number")
        broadcast_group = data.get("broadcast_group")

        message_status = db.query(MessageStatus).filter(
            MessageStatus.business_phone_number_id == business_phone_number_id,
            MessageStatus.user_phone_number == user_phone_number,
            MessageStatus.broadcast_group == broadcast_group
        ).first()

        if not message_status:
            message_status = MessageStatus(
                business_phone_number_id=business_phone_number_id,
                user_phone_number=user_phone_number,
                broadcast_group=broadcast_group,
                broadcast_group_name=data.get("broadcast_group_name"),
                sent=0,
                delivered=0,
                read=0,
                replied=0,
                failed=0,
            )
            db.add(message_status)

        for key in ["sent", "delivered", "read", "replied", "failed"]:
            if key in data and isinstance(data[key], bool):  # Check if key exists and is boolean
                if data[key]:
                    setattr(message_status, key, getattr(message_status, key, 0) + 1)
                else:
                    setattr(message_status, key, max(getattr(message_status, key, 0) - 1, 0))

        
        db.commit()
        db.refresh(message_status)

        return {"message": "Status updated successfully", "data": message_status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

@router.post("/broadcast-groups/", response_model=BroadcastGroupResponse)
def create_group(request: BroadcastGroupCreate, db: orm.Session = Depends(get_db) , x_tenant_id : Optional[str] = Header(None)):
    try:
        members = [member.dict() for member in request.members]

        new_group = BroadcastGroups(
            id=request.id,  # You can generate the ID if not provided
            name=request.name,
            members=members,
            tenant_id = x_tenant_id
        )
        print("New Group: ", request.id, request.name, members)

        db.add(new_group)
        db.commit()
        db.refresh(new_group)

        
        return BroadcastGroupResponse(
            id=new_group.id,
            name=new_group.name,
            members=new_group.members,
            tenant_id = x_tenant_id
        )

    except Exception as e:
        db.rollback()
        print("Error creating groups: ", str(e))
        raise HTTPException(status_code=400, detail="Error in post: creating the broadcast group") from e

@router.get("/broadcast-groups/", response_model=List[BroadcastGroupResponse])
def get_groups(db: orm.Session = Depends(get_db), x_tenant_id : Optional[str] = Header(None)):
    try:
        groups = get_all_broadcast_groups( x_tenant_id,db=db)
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching the broadcast groups") from e


@router.get("/broadcast-groups/{group_id}/", response_model=BroadcastGroupResponse)
def get_group(group_id: str, db: orm.Session = Depends(get_db)):
    try:
        
        group = get_broadcast_group(db=db, group_id=group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Broadcast group not found")
        return group
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching the broadcast group") from e

@router.delete("/broadcast-groups/{group_id}/", response_model=dict)
def delete_group(group_id: str, db: orm.Session = Depends(get_db), x_tenant_id: Optional[str] = Header(None)):
    try:
        # Fetch the group to check existence and tenant ownership
        group = db.query(BroadcastGroups).filter(
            BroadcastGroups.id == group_id, 
            BroadcastGroups.tenant_id == x_tenant_id
        ).first()
        
        if not group:
            raise HTTPException(
                status_code=404, 
                detail="Broadcast group not found or does not belong to the tenant"
            )
        
        # Delete the group
        db.delete(group)
        db.commit()
        
        return {"message": "Broadcast group deleted successfully"}
    
    except Exception as e:
        db.rollback()
        print("Error deleting group:", str(e))
        raise HTTPException(status_code=400, detail="Error deleting the broadcast group") from e