from fastapi import APIRouter, Request, Depends ,HTTPException, Header
from sqlalchemy import orm
from config.database import get_db
from .models import WhatsappTenantData, MessageStatus
from product.models import Product
from typing import Optional

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
        return responses.JSONResponse(content={"whatsapp_data": whatsapp_data_json, "catalog_data": catalog_data_json})

    except Exception as e:
        print("Error occurred with tenant:", x_tenant_id)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    


@router.get("/get-status/")
def get_status(request: Request, db: orm.Session = Depends(get_db)):
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
