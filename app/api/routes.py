
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from app.model.schemas import IDInfo
from app.core.services.id_verification import IDVerificationService
from app.core.logs.logger import logger

router = APIRouter()

@router.post(
    "/verify-id/",
    summary="Verify ID Card",
    description="Upload front and back images of an ID card and provide details to verify against the images."
)
async def verify_id(
    id_info: str = Form(...),
    front_image: UploadFile = File(..., description="Front side of the ID card (JPG, PNG)"),
    back_image: UploadFile = File(..., description="Back side of the ID card (JPG, PNG)")
):
    try:
        # Parse the id_info string as JSON
        try:
             id_info_dict = json.loads(id_info)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in id_info")
            raise HTTPException(status_code=422, detail="Invalid JSON format in id_info")

        # Validate against IDInfo model
        id_info_model = IDInfo(**id_info_dict)

        service = IDVerificationService()
        result = await service.verify_id(id_info_model, front_image, back_image)
        return JSONResponse(content=result)
    except HTTPException as e:
        logger.error(f"HTTP error in /verify-id/: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /verify-id/: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

