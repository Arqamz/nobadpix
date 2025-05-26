from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_database
from app.services import auth_service
from app.models.token import Token as TokenModel
from app.models.usage import Usage as UsageModel
from app.core.config import settings

# This scheme can be used if we decide to make token URL-based for some endpoints
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/tokens") # Example, if using OAuth2 style token issuing endpoint for forms

api_key_header_auth = APIKeyHeader(name="Authorization", auto_error=False)

async def get_current_token(request: Request, token_str: str = Depends(api_key_header_auth), db: AsyncIOMotorDatabase = Depends(get_database)) -> TokenModel:
    print(f"DEBUG: Received Authorization header: '{token_str}'")
    
    if token_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not token_str or not token_str.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Header must start with 'Bearer '.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    actual_token = token_str.split(" ", 1)[1]
    if not actual_token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API token missing after 'Bearer ' scheme. Please provide a valid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_obj = await auth_service.get_token_by_token_string(db, actual_token)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    route_path = "unknown"
    if request.scope.get("route"):
        route_path = request.scope["route"].path

    usage_log = UsageModel(token=actual_token, endpoint=route_path)
    await db[UsageModel.Settings.collection_name].insert_one(usage_log.model_dump(by_alias=True, exclude=["id"]))
    
    return token_obj

async def get_current_active_admin(current_token: TokenModel = Depends(get_current_token)) -> TokenModel:
    if not current_token.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_token

# Dependency for any authenticated user (admin or not)
async def get_current_active_user(current_token: TokenModel = Depends(get_current_token)) -> TokenModel:
    return current_token 