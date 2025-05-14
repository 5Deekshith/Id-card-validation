
from openai import AsyncOpenAI, OpenAIError
from app.model.schemas import IDInfo
from app.core.config.settings import settings
from app.core.logs.logger import logger
from fastapi import HTTPException

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_URL
        )

    async def verify_images(self, id_info: IDInfo, front_image_url: str, back_image_url: str, system_prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Verify the following ID card against this information: {id_info}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": front_image_url,
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": back_image_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ]
            )
            logger.info(f"OpenAI API response: {response}")
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Invalid response structure from OpenAI API")
            return response.choices[0].message.content

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI client: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
