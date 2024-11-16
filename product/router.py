from fastapi import APIRouter, Request, Depends ,HTTPException, Header
from sqlalchemy import orm
from config.database import get_db
from .models import Product
from typing import Optional

router = APIRouter()

@router.get("/catalog/")
def get_catalog(x_tenant_id: Optional[str] = Header(None), db: orm.Session = Depends(get_db)):
    try:
        print("Tenant ID for catalog: ", x_tenant_id)
        catalog = db.query(Product).filter(Product.tenant_id == x_tenant_id).all()
        return catalog
    except Exception as e:
        print("Exception occured in catalog: ", str(e))
        return HTTPException(500, detail=f"An Exception occured in catalog: {str(e)}")