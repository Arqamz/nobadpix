from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import MongoBaseModel

class Token(MongoBaseModel):
    token: str = Field(..., unique=True, index=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    description: Optional[str] = None

    class Settings:
        collection_name = "tokens"

# class TokenInDB(Token): # Removed as it was unused for simple bearer token storage
#     hashed_token: Optional[str] = None 