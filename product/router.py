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

@router.get("/catalog/{product_id}/")
def get_product(product_id = str ,x_tenant_id: Optional[str] = Header(None), db: orm.Session = Depends(get_db)):
    try:
        print("Catalog and Tenant ID rcd: ", product_id, x_tenant_id)
        product  = db.query(Product).filter(Product.tenant_id == x_tenant_id, Product.product_id == product_id).first()

        return product
    except Exception as e:
        print("Exception occured in catalog: ", str(e))
        return HTTPException(500, detail=f"An Exception occured in catalog: {str(e)}")
