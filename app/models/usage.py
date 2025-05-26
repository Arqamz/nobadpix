from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel

class Usage(MongoBaseModel):
    token: str = Field(..., index=True)
    endpoint: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection_name = "usages" 