from fastapi import APIRouter, Request, Depends ,HTTPException, Header
from sqlalchemy import orm
from config.database import get_db
from .models import NodeTemplate
from models import Tenant
from typing import Optional

router = APIRouter()

@router.get('/node-templates/')
def read_nodetemps(request: Request, db: orm.Session = Depends(get_db)):
    tenant_id = request.headers.get("X-Tenant-Id")
    if not tenant_id:
        return HTTPException(status_code=400, detail="Tenant ID is missing in headers")
    if tenant_id == "demo":
        tenant_id = 'ai'

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    node_temps = db.query(NodeTemplate).filter(NodeTemplate.tenant_id == tenant_id).all()

    if not node_temps:
        raise HTTPException(status_code=404, detail="No contacts found for this tenant")

    return node_temps

@router.get("/node-templates/{node_template_id}/")
def get_node_temps(node_template_id : int, x_tenant_id: Optional[str] = Header(None)  ,db: orm.Session = Depends(get_db)):
    if not x_tenant_id:
        return HTTPException(500, detail="Tenant ID is missing")
    tenant = db.query(Tenant).filter(Tenant.id == x_tenant_id).first()
    if not tenant:
        raise HTTPException(400, detail="Tenant Data not found")
    
    node_temp = db.query(NodeTemplate).filter(NodeTemplate.id == node_template_id).first()

    return node_temp
