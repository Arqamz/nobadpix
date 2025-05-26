import secrets
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.db.mongodb import get_database
from app.models.token import Token as TokenModel
from app.schemas.token import TokenCreate, TokenResponse


async def create_access_token_entry(
    db: AsyncIOMotorDatabase, token_data: TokenCreate
) -> TokenResponse:
    token_str = secrets.token_urlsafe(32)
    
    token_obj = TokenModel(
        token=token_str,
        is_admin=token_data.is_admin,
        description=token_data.description,
    )
    result = await db[TokenModel.Settings.collection_name].insert_one(token_obj.model_dump(by_alias=True, exclude=["id"]))
    
    return TokenResponse(
        id=str(result.inserted_id),
        token=token_obj.token,
        is_admin=token_obj.is_admin,
        created_at=token_obj.created_at,
        expires_at=token_obj.expires_at,
        description=token_obj.description
    )

async def get_token_by_token_string(db: AsyncIOMotorDatabase, token_str: str) -> Optional[TokenModel]:
    token_doc = await db[TokenModel.Settings.collection_name].find_one({"token": token_str})
    if token_doc:
        return TokenModel(**token_doc)
    return None

async def get_all_tokens(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[TokenResponse]:
    tokens = []
    cursor = db[TokenModel.Settings.collection_name].find().skip(skip).limit(limit)
    async for doc in cursor:
        tokens.append(TokenResponse(
            id=str(doc["_id"]),
            token=doc["token"],
            is_admin=doc["is_admin"],
            created_at=doc["created_at"],
            expires_at=doc.get("expires_at"),
            description=doc.get("description")
        ))
    return tokens

async def delete_token_by_token_string(db: AsyncIOMotorDatabase, token_str: str) -> bool:
    token_to_delete = await get_token_by_token_string(db, token_str)
    if not token_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    delete_result = await db[TokenModel.Settings.collection_name].delete_one({"token": token_str})
    if delete_result.deleted_count == 1:
        from app.models.usage import Usage as UsageModel 
        await db[UsageModel.Settings.collection_name].delete_many({"token": token_str})
        return True
    if delete_result.deleted_count == 0:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found during delete operation")
    return False 