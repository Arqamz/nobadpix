import pytest
from httpx import AsyncClient
from fastapi import status
import os

# The client fixture is provided by conftest.py

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "<title>nobadpix</title>" in response.text.lower()
    assert "image moderation" in response.text.lower()
    assert "admin panel" in response.text.lower()

@pytest.mark.asyncio
async def test_admin_routes_unauthorized_without_token(client: AsyncClient):
    response = await client.get("/admin/auth/tokens")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "authorization header missing" in response.text.lower() or "authentication required" in response.text.lower()

@pytest.mark.asyncio
async def test_admin_routes_authorized_with_valid_token(client: AsyncClient, admin_bearer_token: str):
    headers = {"Authorization": f"Bearer {admin_bearer_token}"}
    
    response = await client.get("/admin/auth/tokens", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.text.lower() or "admin" in response.text.lower()

    new_token_description = "test-generated-user-token-via-admin"
    response_create = await client.post(
        "/admin/auth/tokens",
        headers=headers,
        data={"is_admin": "false", "description": new_token_description}
    )
    assert response_create.status_code == status.HTTP_200_OK
    assert "successfully created token" in response_create.text.lower()
    assert new_token_description in response_create.text.lower()

    response_get_after_create = await client.get("/admin/auth/tokens", headers=headers)
    assert response_get_after_create.status_code == status.HTTP_200_OK
    assert new_token_description in response_get_after_create.text.lower()

@pytest.mark.asyncio
async def test_moderate_page_unauthorized(client: AsyncClient):
    dummy_image_content = b"fake image data"
    files = {"file": ("test_image.png", dummy_image_content, "image/png")}
    
    response = await client.post("/moderate", files=files)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "authorization header missing" in response.text.lower() or "authentication required" in response.text.lower()

@pytest.mark.asyncio
async def test_initial_admin_token_exists_in_mock_db(client: AsyncClient, mock_mongo_client):
    db_name = os.getenv("DATABASE_NAME", "nobadpix_test")
    db = mock_mongo_client[db_name]
    admin_config_collection = db.get_collection("tokens")
    
    admin_token_doc = await admin_config_collection.find_one({"is_admin": True})
    
    assert admin_token_doc is not None, "No admin token found in the mock database after startup."
    assert "token" in admin_token_doc
    assert admin_token_doc["is_admin"] is True
