from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routers import static_content, admin_auth, moderation
from app.db.mongodb_utils import connect_to_mongo, close_mongo_connection
from app.db.mongodb import get_database
from app.services import auth_service
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.exception_handlers import request_validation_exception_handler

app = FastAPI()

# General Jinja2Templates instance for exception handling if needed globally
# Routers can have their own instances too for their specific template paths.
templates = Jinja2Templates(directory="app/templates")

@app.exception_handler(HTTPException)
async def http_exception_handler_for_htmx(request: Request, exc: HTTPException):
    # Check if the request is likely from our HTMX UI sections
    path = request.url.path
    if path.startswith("/admin/auth/") or path.startswith("/moderate") or path == "/":
        # Attempt to render an HTML error message
        return templates.TemplateResponse("partials/error_message.html", {
            "request": request,
            "error_message": exc.detail,
            "status_code": exc.status_code
        }, status_code=exc.status_code)
    else:
        # Default behavior for other paths (return JSON)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler_for_htmx(request: Request, exc: RequestValidationError):
    path = request.url.path
    if path.startswith("/admin/auth/") or path.startswith("/moderate"):
        error_messages = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error['loc'][1:]) # loc[0] is usually 'body' or 'query'
            message = error['msg']
            error_messages.append(f"Field '{field}': {message}")
        
        return templates.TemplateResponse("partials/error_message.html", {
            "request": request,
            "error_message": "Validation Error: " + "; ".join(error_messages),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    else:
        # Default behavior from FastAPI for validation errors (JSON)
        return await request_validation_exception_handler(request, exc)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    try:
        db = await get_database() # Get database instance
        await admin_auth.ensure_initial_admin_token(db) # Call utility function
    except RuntimeError as e:
        print(f"Error during startup: {e}. This might happen if DB connection failed.")
        # Decide if you want to exit or continue without this setup

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(static_content.router)
app.include_router(admin_auth.router)
app.include_router(moderation.router) 