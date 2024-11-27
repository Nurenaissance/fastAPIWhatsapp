from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import BroadcastGroups
from typing import List, Optional
from .schema import BroadcastGroupMember

# CRUD for creating a BroadcastGroup
def create_broadcast_group(db: Session, name: str,id: str ,members: Optional[List[BroadcastGroupMember]] = []):
    db_group = BroadcastGroups(name=name, id=id, members=members)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

# CRUD for getting a BroadcastGroup by ID
def get_broadcast_group(db: Session, group_id: str):
    return db.query(BroadcastGroups).filter(BroadcastGroups.id == group_id).first()

# CRUD for getting all BroadcastGroups
def get_all_broadcast_groups( tenant_id , db: Session):
    return db.query(BroadcastGroups).filter(BroadcastGroups.tenant_id == tenant_id).all()
