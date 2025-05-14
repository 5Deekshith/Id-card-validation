from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config.settings import settings

app = FastAPI(
    title="ID Card Verification API",
    description="API to verify ID card details against uploaded front and back images using OpenAI's GPT-4o model.",
    version="1.0.0"
)

# Include API routes
app.include_router(api_router, prefix="/api")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         app,
#         host=settings.HOST,
#         port=settings.PORT,
#         log_config=None  # Use custom logging from core.logs.logger
#     )