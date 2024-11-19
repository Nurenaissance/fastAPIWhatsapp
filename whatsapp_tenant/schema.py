from pydantic import BaseModel
from typing import List, Optional

class BroadcastGroupMember(BaseModel):
    name: str
    phone: int  

class BroadcastGroupCreate(BaseModel):
    id: str
    name: str
    members: Optional[List[BroadcastGroupMember]] = []  

class BroadcastGroupResponse(BaseModel):
    id: str
    name: str
    members: Optional[List[dict]] = []

    class Config:
        orm_mode = True
