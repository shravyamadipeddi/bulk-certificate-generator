from pydantic import BaseModel, EmailStr
from typing import List


class RecipientCreate(BaseModel):
    name: str
    email: EmailStr


class GenerationJobCreate(BaseModel):
    event_name: str
    event_date: str
    recipients: List[RecipientCreate]