from fastapi import APIRouter, Request, Depends ,HTTPException, responses
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

@router.patch("/contacts/")
async def update_contact(request: Request, db: orm.Session = Depends(get_db)):
    body = await request.json()  # Parse JSON request body
    contacts = body.get('contact_id', [])
    bg_id = body.get('bgId')
    bg_name = body.get('name')
    errors = []

    for contact_id in contacts:
        try:
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                errors.append(f"Contact with id {contact_id} does not exist.")
                continue

            contact.bg_id = bg_id
            contact.bg_name = bg_name

            db.add(contact)
            db.commit()


        except Exception as e:
            db.rollback()
            errors.append(f"Error updating contact {contact_id}: {str(e)}")

    if errors:
        raise HTTPException(500, detail=errors)
    else:
        return responses.JSONResponse(content=None, status_code=200)
        
    
        
