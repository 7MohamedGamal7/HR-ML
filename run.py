"""
نظام الموارد البشرية الذكي - Smart HR System
نظام متكامل للموارد البشرية يعتمد على الذكاء الاصطناعي
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger
import sys
import os

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION, LOG_FILE
from app.i18n import get_message

# إعداد السجلات - Setup logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")
logger.add(LOG_FILE, rotation="10 MB", retention="30 days", compression="zip", encoding="utf-8")

# إنشاء التطبيق - Create application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# إضافة CORS - Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج، حدد النطاقات المسموحة - In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# استيراد الموجهات - Import routers
from routers import upload, train, predict, policies, hr_operations, health

# تسجيل الموجهات - Register routers
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(train.router)
app.include_router(predict.router)
app.include_router(policies.router)
app.include_router(hr_operations.router)

# خدمة الملفات الثابتة - Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["الرئيسية - Home"])
def root():
    """
    الصفحة الرئيسية - Home page
    """
    return {
        "message": get_message("system_running"),
        "message_en": "Smart HR System is running. Visit /docs for Swagger UI.",
        "version": API_VERSION,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/upload",
            "train": "/train",
            "predict": "/predict",
            "policies": "/policies",
            "hr": "/hr",
            "database_ui": "/static/database_connection.html"
        }
    }


@app.on_event("startup")
async def startup_event():
    """حدث بدء التشغيل - Startup event"""
    logger.info("=" * 60)
    logger.info(f"🚀 بدء تشغيل {API_TITLE}")
    logger.info(f"📌 الإصدار: {API_VERSION}")
    logger.info(f"📚 الوثائق: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """حدث إيقاف التشغيل - Shutdown event"""
    logger.info("⏹️  إيقاف النظام...")


if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
