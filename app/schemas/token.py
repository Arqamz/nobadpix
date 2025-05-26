from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TokenCreate(BaseModel):
    is_admin: bool = False
    description: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    is_admin: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    description: Optional[str] = None
    id: str # The MongoDB document ID as a string

class TokenMinimal(BaseModel):
    token: str
    is_admin: bool 