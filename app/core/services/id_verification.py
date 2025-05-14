import json
from fastapi import HTTPException, UploadFile
from app.model.schemas import IDInfo
from app.core.integrations.openai_client import OpenAIClient
from app.core.config.settings import settings
from app.core.logs.logger import logger
import base64

class IDVerificationService:
    def __init__(self):
        self.openai_client = OpenAIClient()

    async def _validate_image(self, image: UploadFile) -> tuple[bytes, str]:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image (JPG, PNG).")

        try:
            image_data = await image.read()
        except Exception as e:
            logger.error(f"Failed to read image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to read image: {str(e)}")

        if len(image_data) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit.")

        image_format = image.filename.split(".")[-1].lower()
        if image_format not in settings.ALLOWED_IMAGE_FORMATS:
            raise HTTPException(status_code=400, detail="Unsupported image format. Use JPG or PNG.")

        return image_data, image_format

    async def verify_id(self, id_info: IDInfo, front_image: UploadFile, back_image: UploadFile) -> dict:
        front_data, front_format = await self._validate_image(front_image)
        back_data, back_format = await self._validate_image(back_image)

        front_url = self._get_image_data_url(front_data, front_format)
        back_url = self._get_image_data_url(back_data, back_format)

        system_prompt = """
You are an expert ID verification assistant. Your task is to analyze the front and back images of an ID card (College ID, Employee ID, or Industry ID) and verify whether the details on the ID match the provided information.

You will receive:
1. Front and back images of the ID card.
2. A dictionary containing the expected details (e.g., name, ID number, organization, type, and optionally date of birth).

**Instructions:**
- Extract the following details from the ID card images: name, ID number, organization, type (must be 'College ID', 'Employee ID', or 'Industry ID'), and date of birth (if present).
- Compare the extracted details with the provided dictionary.
- Return a JSON object with:
  - A boolean field `is_verified` indicating whether all provided details match the ID card.
  - A `details` field explaining which fields matched or mismatched, noting which image (front or back) provided the information.
  - A `confidence` field (0 to 1) indicating your confidence in the extracted information from the images.
- If any information cannot be extracted from the images, note it in the `details` field and set `is_verified` to false.
- If the images are unclear or not an ID card, return an appropriate error message in the `details` field.

**Example Output:**
```json
{
  "is_verified": true,
  "details": "All fields (name, ID number, organization, type) matched the provided information. Name and ID number extracted from front image, organization from back image.",
  "confidence": 0.95
}
```
"""
        try:
            response = await self.openai_client.verify_images(
                id_info=id_info,
                front_image_url=front_url,
                back_image_url=back_url,
                system_prompt=system_prompt
            )
            print(response)
            return response
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to parse model response as JSON.")

    async def validate_id(self, id_info: IDInfo, front_image: UploadFile, back_image: UploadFile) -> dict:
        front_data, front_format = await self._validate_image(front_image)
        back_data, back_format = await self._validate_image(back_image)

        front_url = self._get_image_data_url(front_data, front_format)
        back_url = self._get_image_data_url(back_data, back_format)

        system_prompt = """
You are an expert ID validation assistant. Your task is to analyze the front and back images of an ID card (College ID, Employee ID, or Industry ID) and validate whether the details match the provided information.

You will receive:
1. Front and back images of the ID card.
2. A dictionary containing the expected details (e.g., name, ID number, organization, type, and optionally date of birth).

**Instructions:**
- Extract the details: name, ID number, organization, type (must be 'College ID', 'Employee ID', or 'Industry ID'), and date of birth (if present).
- Compare with the provided dictionary.
- Return a JSON object with:
  - `is_valid`: Boolean indicating if all details match.
  - `message`: Explanation of the validation result.
  - `card_type`: The type of ID (e.g., 'student', 'employee', 'industry').
  - `details`: Object with field-specific validation results (e.g., {'name': true, 'id_number': false}).
- If information cannot be extracted, note it in `message` and set `is_valid` to false.

**Example Output:**
```json
{
  "is_valid": true,
  "message": "All fields matched the provided information.",
  "card_type": "student",
  "details": {
    "name": true,
    "id_number": true,
    "organization": true,
    "type": true
  }
}
```
"""
        try:
            response = await self.openai_client.verify_images(
                id_info=id_info,
                front_image_url=front_url,
                back_image_url=back_url,
                system_prompt=system_prompt
            )
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to parse model response as JSON.")

    @staticmethod
    def _get_image_data_url(image_data: bytes, image_format: str) -> str:
        try:
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            return f"data:image/{image_format};base64,{image_base64}"
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to encode image: {str(e)}")
