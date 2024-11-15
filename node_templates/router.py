from fastapi import APIRouter, Request, Depends ,HTTPException
from sqlalchemy import orm
from config.database import get_db
from .models import NodeTemplate
from models import Tenant

router = APIRouter()

@router.get('/node-templates/')
def read_nodetemps(request: Request, db: orm.Session = Depends(get_db)):
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
