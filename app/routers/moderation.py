from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil # For saving file, if needed, or working with temp files
import secrets
import datetime # Import datetime
import base64 # For image preview

from app.dependencies import get_current_active_user # Any valid token
from app.models.token import Token as TokenModel
from app.services.moderation_service import azure_moderation_service # Import the new service
from app.utils.plotting import generate_severity_plot_base64 # Import the plotting function

router = APIRouter(
    prefix="/moderate",
    tags=["Image Moderation"],
    dependencies=[Depends(get_current_active_user)] # Protects all routes in this router
)

templates = Jinja2Templates(directory="app/templates") # Assuming templates are in app/templates

@router.post("", response_class=HTMLResponse) # POST /moderate
async def moderate_image_route(
    request: Request,
    file: UploadFile = File(...),
    current_user: TokenModel = Depends(get_current_active_user) # Injects the token model for the authenticated user
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type. Please upload an image.")

    image_bytes = await file.read()
    await file.seek(0) # Reset cursor in case file is used again, though we close it here.
    
    # Create Base64 preview
    # For very large images, you might want to resize before encoding, 
    # but for now, we encode the original.
    image_base64_preview = base64.b64encode(image_bytes).decode("utf-8")
    # Limit preview string length if necessary, but typically it's fine for HTML attributes.

    await file.close()

    # Call the Azure Moderation Service
    azure_report = await azure_moderation_service.analyze_image(image_bytes)
    severity_plot_base64 = None

    if azure_report.get("error"):
        # Handle error from Azure service - potentially raise HTTPException or format for error_message.html
        # For now, let's pass it to the report to be displayed.
        # Consider a more robust error display for production.
        report = {
            "filename": file.filename,
            "content_type": file.content_type,
            "is_safe_overall": False,
            "categories": {},
            "message": azure_report.get("message", "An error occurred during moderation."),
            "error_details": azure_report.get("details"),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "image_base64_preview": image_base64_preview,
            "severity_plot_base64": severity_plot_base64
        }
    else:
        # Generate plot only if no error and categories are present
        if azure_report.get("categories"):
            try:
                severity_plot_base64 = generate_severity_plot_base64(azure_report["categories"])
            except Exception as e:
                print(f"Error generating severity plot: {e}") # Log error, don't crash
                # severity_plot_base64 remains None

        report = {
            "filename": file.filename,
            "content_type": file.content_type,
            "is_safe_overall": azure_report["is_safe_overall"],
            "categories": azure_report["categories"], # This will now have keys like 'hate', 'self_harm', etc.
            "message": "Image processed successfully." if azure_report["is_safe_overall"] else "Image flagged for potential issues.",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "image_base64_preview": image_base64_preview,
            "severity_plot_base64": severity_plot_base64
            # We are not getting overall_confidence directly from this basic Azure SDK mapping
            # If needed, this could be derived or a default set.
        }

    # Render an HTML partial to display the report for HTMX
    # The target div in index.html will be updated by this response.
    return templates.TemplateResponse("partials/moderation_report.html", {"request": request, "report": report}) 