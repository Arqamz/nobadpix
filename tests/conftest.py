import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from mongomock_motor import AsyncMongoMockClient
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def mock_mongo_client():
    client = AsyncMongoMockClient()
    return client

@pytest.fixture(scope="function")
async def app_instance(mock_mongo_client, monkeypatch):
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    monkeypatch.setenv("DATABASE_NAME", "nobadpix_test")
    monkeypatch.setenv("ADMIN_TOKEN_STRING", "test_admin_token_for_ensure_initial_admin_if_it_used_it_but_it_doesnt")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key_for_jwt_if_needed_elsewhere")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    modules_to_reload = [
        "app.core.config",
        "app.db.mongodb",
        "app.db.mongodb_utils",
        "app.services.auth_service",
        "app.dependencies",
        "app.routers.admin_auth",
        "app.routers.moderation",
        "app.main"
    ]
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            del sys.modules[module_name]

    from app.db import mongodb_utils, mongodb
    from app.core.config import settings

    mongodb_utils.db.client = mock_mongo_client
    
    async def mock_get_database():
        db_name = os.getenv("DATABASE_NAME", "nobadpix_test")
        return mock_mongo_client[db_name]
    
    async def mock_connect_to_mongo():
        print("Mocked connect_to_mongo called")
        pass

    async def mock_close_mongo_connection():
        print("Mocked close_mongo_connection called")
        pass

    monkeypatch.setattr(mongodb_utils, "connect_to_mongo", mock_connect_to_mongo)
    monkeypatch.setattr(mongodb_utils, "close_mongo_connection", mock_close_mongo_connection)
    monkeypatch.setattr(mongodb, "get_database", mock_get_database)
    
    from app.main import app as main_app
    from app.routers.admin_auth import ensure_initial_admin_token
    
    db = await mock_get_database()
    await ensure_initial_admin_token(db)
    
    main_app.test_mock_mongo_client = mock_mongo_client
    
    return main_app


@pytest.fixture(scope="function")
async def client(app_instance: FastAPI):
    async with AsyncClient(transport=ASGITransport(app=app_instance), base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function")
async def admin_bearer_token(app_instance: FastAPI):
    from app.services.auth_service import get_all_tokens
    
    db_name = os.getenv("DATABASE_NAME", "nobadpix_test")
    mock_mongo_client = app_instance.test_mock_mongo_client
    db = mock_mongo_client[db_name]
    
    admin_tokens = [t for t in await get_all_tokens(db) if t.is_admin]
    
    if not admin_tokens:
        print("WARN: No admin token found after startup, attempting to create one explicitly for test.")
        from app.routers.admin_auth import ensure_initial_admin_token
        await ensure_initial_admin_token(db) 
        admin_tokens = [t for t in await get_all_tokens(db) if t.is_admin]
        if not admin_tokens:
            pytest.fail("Failed to create or find admin bearer token in mock DB even after explicit call.")

    token_str = admin_tokens[0].token
    print(f"Using admin bearer token for test: {token_str}")
    return token_str 