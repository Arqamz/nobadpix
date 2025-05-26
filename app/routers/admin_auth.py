from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_database
from app.services import auth_service
from app.schemas.token import TokenCreate, TokenResponse
from app.dependencies import get_current_active_admin, get_current_active_user
from app.models.token import Token as TokenModel # For dependency injection type hint

router = APIRouter(
    prefix="/admin/auth",
    tags=["Admin Authentication"],
    dependencies=[Depends(get_current_active_admin)]
)

templates = Jinja2Templates(directory="app/templates")


@router.post("/tokens", response_class=HTMLResponse)
async def create_token_for_admin_route(
    request: Request,
    is_admin: bool = Form(False),
    description: Optional[str] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin_user: TokenModel = Depends(get_current_active_admin)
):
    token_create_schema = TokenCreate(is_admin=is_admin, description=description)
    new_token = await auth_service.create_access_token_entry(db, token_create_schema)
    
    all_tokens = await auth_service.get_all_tokens(db, limit=100)
    
    new_token_html_message = f'''
    <div class="alert alert-success alert-dismissible fade show" role="alert">
        <strong>Successfully created token:</strong> <code class="token-value">{new_token.token}</code>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    '''
    
    token_list_html = templates.get_template("partials/admin_tokens.html").render(
        {"request": request, "tokens": all_tokens, "new_token_message": new_token_html_message}
    )
    
    return templates.TemplateResponse(
        "partials/admin_dashboard_content.html",
        {
            "request": request,
            "existing_tokens_html": token_list_html,
            # Optionally, pass the raw message too if dashboard wants to display it separately
            # "new_token_message_raw": new_token_html_message 
        }
    )


@router.get("/tokens", response_class=HTMLResponse)
async def read_tokens_for_admin_route(
    request: Request, 
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin_user: TokenModel = Depends(get_current_active_admin)
):
    tokens = await auth_service.get_all_tokens(db, limit=100)
    
    token_list_html = templates.get_template("partials/admin_tokens.html").render(
        {"request": request, "tokens": tokens}
    )
    
    return templates.TemplateResponse(
        "partials/admin_dashboard_content.html",
        {"request": request, "existing_tokens_html": token_list_html}
    )


@router.delete("/tokens/{token_to_delete}", response_class=HTMLResponse)
async def delete_token_for_admin_route(
    request: Request, 
    token_to_delete: str, 
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin_user: TokenModel = Depends(get_current_active_admin)
):
    try:
        await auth_service.delete_token_by_token_string(db, token_to_delete)
        message = f'''
        <div class="alert alert-info alert-dismissible fade show" role="alert">
            Token <code>{token_to_delete}</code> deleted successfully.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        '''
    except HTTPException as e:
        message = f'''
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <strong>Error deleting token:</strong> {e.detail}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        '''
    
    tokens = await auth_service.get_all_tokens(db, limit=100)
    
    token_list_html = templates.get_template("partials/admin_tokens.html").render(
        {"request": request, "tokens": tokens, "new_token_message": message}
    )

    return templates.TemplateResponse(
        "partials/admin_dashboard_content.html",
        {"request": request, "existing_tokens_html": token_list_html}
    )

async def ensure_initial_admin_token(db: AsyncIOMotorDatabase):
    all_db_tokens = await auth_service.get_all_tokens(db, limit=10)
    is_admin_token_present = False
    if all_db_tokens:
        for token_resp in all_db_tokens:
            if token_resp.is_admin:
                is_admin_token_present = True
                break
    
    if not is_admin_token_present:
        print("No admin tokens found. Creating an initial admin token.")
        initial_admin_token_data = TokenCreate(is_admin=True, description="Initial admin token")
        new_token = await auth_service.create_access_token_entry(db, initial_admin_token_data)
        print("======================================================================================")
        print(f"INITIAL ADMIN TOKEN (Save this securely! This will only be shown once.):")
        print(f"Bearer {new_token.token}")
        print("Description: Initial admin token")
        print("======================================================================================")
    else:
        print("Admin token(s) already exist. Skipping initial token creation.") 