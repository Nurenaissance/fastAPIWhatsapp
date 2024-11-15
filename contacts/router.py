from fastapi import APIRouter, Request, Depends ,HTTPException
from sqlalchemy import orm
from config.database import get_db
from .models import Contact
from models import Tenant

router = APIRouter()


@router.get("/contacts/")
def read_contacts(request: Request, db: orm.Session = Depends(get_db)):
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
