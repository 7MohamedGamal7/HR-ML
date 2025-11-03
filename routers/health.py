"""
موجه الفحص الصحي - Health Check Router
يوفر نقاط نهاية لفحص صحة النظام
"""

from fastapi import APIRouter, Query
from typing import Dict, Any
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

from app.config import (
    DATA_DIR, MODELS_DIR, LOGS_DIR, POLICIES_DIR,
    PROMOTION_MODEL_PATH, API_VERSION
)
from app.i18n import get_message

router = APIRouter(prefix="/health", tags=["الفحص الصحي - Health"])


@router.get("/")
async def health_check(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    فحص صحة النظام - System health check
    
    Args:
        lang: اللغة - Language
    
    Returns:
        حالة النظام - System status
    """
    try:
        # فحص المجلدات - Check directories
        directories_status = {
            "data": DATA_DIR.exists(),
            "models": MODELS_DIR.exists(),
            "logs": LOGS_DIR.exists(),
            "policies": POLICIES_DIR.exists()
        }
        
        # فحص النموذج - Check model
        model_exists = PROMOTION_MODEL_PATH.exists()
        
        # فحص البيانات - Check dataset
        dataset_path = DATA_DIR / "cleaned_dataset.csv"
        dataset_exists = dataset_path.exists()
        
        # حساب الحالة العامة - Calculate overall status
        all_dirs_ok = all(directories_status.values())
        is_healthy = all_dirs_ok
        
        status = {
            "status": "healthy" if is_healthy else "degraded",
            "message": get_message("system_healthy", lang) if is_healthy else "النظام يعمل بشكل جزئي" if lang == "ar" else "System partially operational",
            "version": API_VERSION,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "directories": directories_status,
                "model_trained": model_exists,
                "dataset_uploaded": dataset_exists
            }
        }
        
        return status
    
    except Exception as e:
        logger.error(f"خطأ في فحص الصحة: {e}")
        return {
            "status": "unhealthy",
            "message": get_message("error", lang),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/detailed")
async def detailed_health_check(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    فحص صحة مفصل - Detailed health check
    
    Args:
        lang: اللغة - Language
    
    Returns:
        حالة النظام المفصلة - Detailed system status
    """
    try:
        # معلومات المجلدات - Directory information
        def get_dir_info(path: Path) -> Dict[str, Any]:
            if not path.exists():
                return {"exists": False, "files": 0, "size_mb": 0}
            
            files = list(path.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            return {
                "exists": True,
                "files": len(files),
                "size_mb": round(total_size / (1024 * 1024), 2)
            }
        
        # معلومات النموذج - Model information
        model_info = {}
        if PROMOTION_MODEL_PATH.exists():
            model_stat = PROMOTION_MODEL_PATH.stat()
            model_info = {
                "exists": True,
                "size_mb": round(model_stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(model_stat.st_mtime).isoformat()
            }
        else:
            model_info = {"exists": False}
        
        # معلومات البيانات - Dataset information
        dataset_path = DATA_DIR / "cleaned_dataset.csv"
        dataset_info = {}
        if dataset_path.exists():
            dataset_stat = dataset_path.stat()
            dataset_info = {
                "exists": True,
                "size_mb": round(dataset_stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(dataset_stat.st_mtime).isoformat()
            }
        else:
            dataset_info = {"exists": False}
        
        # معلومات السياسات - Policies information
        from app.policy_manager import policy_manager
        policies_stats = policy_manager.get_statistics()
        
        # معلومات النظام - System information
        import platform
        system_info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "machine": platform.machine()
        }
        
        return {
            "status": "healthy",
            "message": get_message("system_healthy", lang),
            "version": API_VERSION,
            "timestamp": datetime.now().isoformat(),
            "directories": {
                "data": get_dir_info(DATA_DIR),
                "models": get_dir_info(MODELS_DIR),
                "logs": get_dir_info(LOGS_DIR),
                "policies": get_dir_info(POLICIES_DIR)
            },
            "model": model_info,
            "dataset": dataset_info,
            "policies": policies_stats,
            "system": system_info
        }
    
    except Exception as e:
        logger.error(f"خطأ في الفحص الصحي المفصل: {e}")
        return {
            "status": "error",
            "message": get_message("error", lang),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/readiness")
async def readiness_check():
    """
    فحص الجاهزية - Readiness check (for Kubernetes/Docker)
    
    Returns:
        حالة الجاهزية - Readiness status
    """
    try:
        # التحقق من المتطلبات الأساسية - Check basic requirements
        ready = (
            DATA_DIR.exists() and
            MODELS_DIR.exists() and
            LOGS_DIR.exists()
        )
        
        if ready:
            return {"status": "ready"}
        else:
            return {"status": "not_ready"}, 503
    
    except Exception:
        return {"status": "not_ready"}, 503


@router.get("/liveness")
async def liveness_check():
    """
    فحص الحياة - Liveness check (for Kubernetes/Docker)
    
    Returns:
        حالة الحياة - Liveness status
    """
    return {"status": "alive"}

