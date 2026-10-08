from pydantic import BaseModel, EmailStr, Field
from datetime import date


class RecipientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class GenerationJobCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    course_name: str = Field(min_length=2, max_length=200)
    date: date
    recipients: list[RecipientCreate] = Field(min_length=1)