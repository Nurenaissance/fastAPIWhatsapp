from pydantic import BaseModel
from datetime import datetime
from config.database import Base
from sqlalchemy import orm, Column, Integer, String
from fastapi import APIRouter, Depends, HTTPException
from config.database import get_db
from typing import List

router = APIRouter()

class EmailEntry(Base):
    __tablename__ = "email_entry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    date_created = Column(String, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<EmailEntry(email={self.email}, date_created={self.date_created})>"

# Define the Pydantic model for input
class EmailInput(BaseModel):
    email: str  # Using str instead of EmailStr

# Define the Pydantic model for output
class EmailResponse(BaseModel):
    email: str  # Using str instead of EmailStr
    date_created: datetime

@router.post("/add_email", response_model=EmailResponse)
def add_email(email_input: EmailInput, db: orm.Session = Depends(get_db)):
    # Check for duplicates
    existing_email = db.query(EmailEntry).filter(EmailEntry.email == email_input.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create a new email entry
    new_email = EmailEntry(email=email_input.email, date_created=datetime.utcnow().isoformat())
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    return new_email

@router.get("/emails", response_model=List[EmailResponse])
def get_emails(db: orm.Session = Depends(get_db)):
    emails = db.query(EmailEntry).all()
    return emails
