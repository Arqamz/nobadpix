from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

from app.core.config import settings

class AzureModerationService:
    def __init__(self):
        if not settings.AZURE_CONTENT_SAFETY_ENDPOINT or not settings.AZURE_CONTENT_SAFETY_KEY:
            raise ValueError("Azure Content Safety Endpoint or Key is not configured.")
        
        self.client = ContentSafetyClient(
            endpoint=settings.AZURE_CONTENT_SAFETY_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_CONTENT_SAFETY_KEY)
        )

    async def analyze_image(self, image_bytes: bytes) -> dict:
        image_data = ImageData(content=image_bytes)
        # Default outputType is FourSeverityLevels, which returns 0, 2, 4, 6
        request = AnalyzeImageOptions(image=image_data) 
        
        try:
            response = self.client.analyze_image(request)
        except HttpResponseError as e:
            print(f"Azure Content Safety API error: {e}")
            # Depending on how you want to surface this, you could raise a custom exception
            # or return a specific error structure.
            return {
                "error": True,
                "message": f"Error analyzing image with Azure Content Safety: {e.message}",
                "details": str(e)
            }

        # Process the response into a more friendly format
        # Azure SDK returns severity for categories like Hate, SelfHarm, Sexual, Violence
        # Severity ranges from 0 (Very Low) to 6 (Very High), or can be higher.
        # For simplicity, we'll directly map them.
        
        analysis_result = {"categories": {}, "is_safe_overall": True, "error": False}
        
        if response.categories_analysis:
            for category_analysis in response.categories_analysis:
                category_name = category_analysis.category.lower() # e.g. "hate", "sexual"
                severity = category_analysis.severity
                analysis_result["categories"][category_name] = severity
                
                # Assuming any severity greater than 0 means it's not safe for that category.
                # Azure's FourSeverityLevels are 0, 2, 4, 6.
                # 0 = Not detected / Very Low
                # 2 = Low
                # 4 = Medium
                # 6 = High
                # Adjust this threshold if needed, e.g., if only 4 and 6 are considered unsafe.
                if severity > 0: 
                    analysis_result["is_safe_overall"] = False
        
        return analysis_result

# Singleton instance
azure_moderation_service = AzureModerationService() 