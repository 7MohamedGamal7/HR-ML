"""
موجه التدريب - Training Router
يوفر نقاط نهاية لتدريب النماذج
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from loguru import logger
import os
import json

from app.config import DATA_DIR
from app.data_utils import (
    split_data, validate_dataframe, prepare_employee_data,
    clean_df, create_promotion_target
)
from app.model_utils import (
    build_and_train, evaluate, save_model, get_feature_importance
)
from app.i18n import get_message
from app.database import db

router = APIRouter(prefix="/train", tags=["التدريب - Training"])


class TrainingConfig(BaseModel):
    """تكوين التدريب - Training configuration"""
    model_type: str = "random_forest"
    use_cross_validation: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "random_forest",
                "use_cross_validation": True
            }
        }


class DatabaseConfig(BaseModel):
    """تكوين قاعدة البيانات - Database configuration"""
    host: str
    port: int = 1433
    database: str
    username: str
    password: str
    driver: str = "ODBC Driver 17 for SQL Server"
    timeout: int = 30
    default_table: str = "Employees"

    class Config:
        json_schema_extra = {
            "example": {
                "host": "localhost",
                "port": 1433,
                "database": "HR_Database",
                "username": "sa",
                "password": "YourPassword123!",
                "driver": "ODBC Driver 17 for SQL Server",
                "timeout": 30,
                "default_table": "Employees"
            }
        }


@router.post("/")
async def train_model(
    config: Optional[TrainingConfig] = None,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    تدريب نموذج التنبؤ بالترقيات - Train promotion prediction model

    Args:
        config: تكوين التدريب - Training configuration
        lang: اللغة - Language

    Returns:
        نتائج التدريب والمقاييس - Training results and metrics
    """
    try:
        # التحقق من وجود البيانات - Check for dataset
        path = DATA_DIR / "cleaned_dataset.csv"
        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail=get_message("no_dataset", lang)
            )

        # قراءة البيانات - Read dataset
        logger.info("قراءة مجموعة البيانات...")
        df = pd.read_csv(path, encoding='utf-8')

        if df.empty:
            raise HTTPException(
                status_code=422,
                detail=get_message("dataset_empty", lang)
            )

        # التحقق من صحة البيانات - Validate dataset
        is_valid, errors = validate_dataframe(df, require_target=True)
        if not is_valid:
            raise HTTPException(
                status_code=422,
                detail=f"{get_message('invalid_input', lang)}: {', '.join(errors)}"
            )

        # تقسيم البيانات - Split data
        logger.info("تقسيم البيانات...")
        X_train, X_test, y_train, y_test = split_data(df)

        # تدريب النموذج - Train model
        logger.info("بدء تدريب النموذج...")

        if config is None:
            config = TrainingConfig()

        model = build_and_train(
            X_train, y_train,
            model_type=config.model_type,
            use_cross_validation=config.use_cross_validation
        )

        # تقييم النموذج - Evaluate model
        logger.info("تقييم النموذج...")
        metrics = evaluate(model, X_test, y_test, detailed=True)

        # حفظ النموذج - Save model
        logger.info("حفظ النموذج...")
        save_model(
            model,
            metadata={
                "model_type": config.model_type,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
        )

        # الحصول على أهمية المتغيرات - Get feature importance
        feature_importance = get_feature_importance(model)

        logger.info("اكتمل التدريب بنجاح!")

        return {
            "detail": get_message("training_completed", lang),
            "message": get_message("model_saved", lang),
            "metrics": {
                get_message("accuracy", lang): metrics.get("accuracy"),
                get_message("precision", lang): metrics.get("precision"),
                get_message("recall", lang): metrics.get("recall"),
                get_message("f1_score", lang): metrics.get("f1_score"),
            },
            "full_metrics": metrics,
            "feature_importance": feature_importance,
            "training_info": {
                "model_type": config.model_type,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "total_features": X_train.shape[1]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في التدريب: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("training_error", lang, error=str(e))
        )


@router.post("/from-database")
async def train_from_database(
    table_name: Optional[str] = Query(None, description="اسم الجدول - Table name"),
    query: Optional[str] = Query(None, description="استعلام SQL مخصص - Custom SQL query"),
    limit: Optional[int] = Query(None, description="حد عدد الصفوف - Row limit"),
    config: Optional[TrainingConfig] = None,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    تدريب النموذج من قاعدة بيانات SQL Server - Train model from SQL Server database

    Args:
        table_name: اسم الجدول - Table name (optional)
        query: استعلام SQL مخصص - Custom SQL query (optional)
        limit: حد عدد الصفوف - Row limit (optional)
        config: تكوين التدريب - Training configuration
        lang: اللغة - Language

    Returns:
        نتائج التدريب والمقاييس - Training results and metrics
    """
    try:
        logger.info("=" * 60)
        logger.info("بدء التدريب من قاعدة البيانات - Starting training from database")

        # اختبار الاتصال بقاعدة البيانات
        connection_test = db.test_connection()
        if not connection_test["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"فشل الاتصال بقاعدة البيانات - Database connection failed: {connection_test.get('message', 'Unknown error')}"
            )

        logger.info(f"✅ الاتصال بقاعدة البيانات ناجح - {connection_test.get('server', 'Unknown')}")

        # تحميل البيانات من قاعدة البيانات
        logger.info("تحميل بيانات الموظفين من قاعدة البيانات...")
        df = db.load_employee_data(table_name=table_name, query=query, limit=limit)

        if df.empty:
            raise HTTPException(
                status_code=422,
                detail=get_message("dataset_empty", lang)
            )

        logger.info(f"تم تحميل {len(df)} موظف، {len(df.columns)} عمود")

        # تحضير البيانات
        logger.info("تحضير بيانات الموظفين...")
        df = prepare_employee_data(df)

        # تنظيف البيانات
        logger.info("تنظيف البيانات...")
        df = clean_df(df)

        # إنشاء عمود الهدف (promotion_eligible)
        logger.info("إنشاء عمود الهدف...")
        df = create_promotion_target(df)

        # حفظ البيانات المنظفة
        cleaned_path = DATA_DIR / "cleaned_dataset.csv"
        df.to_csv(cleaned_path, index=False, encoding='utf-8')
        logger.info(f"تم حفظ البيانات المنظفة: {cleaned_path}")

        # التحقق من صحة البيانات
        is_valid, errors = validate_dataframe(df, require_target=True)
        if not is_valid:
            logger.warning(f"تحذيرات في البيانات: {errors}")
            # نكمل التدريب مع التحذيرات

        # تقسيم البيانات
        logger.info("تقسيم البيانات...")
        X_train, X_test, y_train, y_test = split_data(df)

        logger.info(f"حجم بيانات التدريب: {len(X_train)}")
        logger.info(f"حجم بيانات الاختبار: {len(X_test)}")

        # تحديد نوع النموذج
        model_type = config.model_type if config else "random_forest"
        use_cv = config.use_cross_validation if config else True

        # بناء وتدريب النموذج
        logger.info(f"بناء وتدريب النموذج ({model_type})...")
        model, pipeline = build_and_train(
            X_train, y_train,
            model_type=model_type,
            use_cross_validation=use_cv
        )

        # تقييم النموذج
        logger.info("تقييم النموذج...")
        metrics = evaluate(pipeline, X_test, y_test)

        # حفظ النموذج
        logger.info("حفظ النموذج...")
        save_model(pipeline, metrics)

        # الحصول على أهمية الميزات
        feature_importance = get_feature_importance(pipeline, X_train.columns)

        logger.info("=" * 60)
        logger.info("✅ اكتمل التدريب بنجاح من قاعدة البيانات!")
        logger.info(f"الدقة: {metrics['accuracy']:.2%}")
        logger.info("=" * 60)

        return {
            "detail": get_message("training_success", lang),
            "message": "تم التدريب بنجاح من قاعدة البيانات - Training completed successfully from database",
            "data_source": {
                "type": "SQL Server Database",
                "table_name": table_name or "Custom Query",
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "training_rows": len(X_train),
                "testing_rows": len(X_test)
            },
            "metrics": {
                "accuracy": round(metrics["accuracy"], 4),
                "precision": round(metrics["precision"], 4),
                "recall": round(metrics["recall"], 4),
                "f1_score": round(metrics["f1"], 4),
                "roc_auc": round(metrics.get("roc_auc", 0), 4)
            },
            "model_info": {
                "type": model_type,
                "cross_validation": use_cv,
                "features_count": len(X_train.columns)
            },
            "feature_importance": feature_importance[:10],  # أهم 10 ميزات
            "data_warnings": errors if not is_valid else []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في التدريب من قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في التدريب من قاعدة البيانات - Database training error: {str(e)}"
        )


@router.get("/database/test-connection")
async def test_database_connection(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    اختبار الاتصال بقاعدة البيانات - Test database connection

    Returns:
        نتيجة الاختبار - Test result
    """
    try:
        result = db.test_connection()

        if result["success"]:
            return {
                "detail": "الاتصال بقاعدة البيانات ناجح - Database connection successful",
                "connection_info": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"فشل الاتصال بقاعدة البيانات - Connection failed: {result.get('message', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في اختبار الاتصال: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في اختبار الاتصال - Connection test error: {str(e)}"
        )


@router.get("/database/tables")
async def list_database_tables(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    الحصول على قائمة الجداول في قاعدة البيانات - Get list of database tables

    Returns:
        قائمة الجداول - List of tables
    """
    try:
        tables = db.list_tables()

        return {
            "detail": f"تم العثور على {len(tables)} جدول - Found {len(tables)} tables",
            "tables": tables,
            "count": len(tables)
        }

    except Exception as e:
        logger.error(f"خطأ في الحصول على قائمة الجداول: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في الحصول على قائمة الجداول - Error listing tables: {str(e)}"
        )


@router.get("/database/table-info")
async def get_table_info(
    table_name: str = Query(..., description="اسم الجدول - Table name"),
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    الحصول على معلومات جدول محدد - Get information about a specific table

    Args:
        table_name: اسم الجدول - Table name

    Returns:
        معلومات الجدول - Table information
    """
    try:
        info = db.get_table_info(table_name)

        return {
            "detail": f"معلومات الجدول {table_name} - Table {table_name} information",
            "table_info": info
        }

    except Exception as e:
        logger.error(f"خطأ في الحصول على معلومات الجدول: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في الحصول على معلومات الجدول - Error getting table info: {str(e)}"
        )


@router.post("/database/save-config")
async def save_database_config(
    config: DatabaseConfig,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    حفظ إعدادات قاعدة البيانات - Save database configuration

    Args:
        config: إعدادات قاعدة البيانات - Database configuration

    Returns:
        رسالة تأكيد - Confirmation message
    """
    try:
        # حفظ الإعدادات في ملف JSON
        config_path = os.path.join("data", "db_config.json")
        os.makedirs("data", exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)

        logger.info(f"تم حفظ إعدادات قاعدة البيانات في {config_path}")

        # تحديث متغيرات البيئة
        os.environ['SQL_SERVER_HOST'] = config.host
        os.environ['SQL_SERVER_PORT'] = str(config.port)
        os.environ['SQL_SERVER_DATABASE'] = config.database
        os.environ['SQL_SERVER_USERNAME'] = config.username
        os.environ['SQL_SERVER_PASSWORD'] = config.password
        os.environ['SQL_SERVER_DRIVER'] = config.driver
        os.environ['SQL_SERVER_TIMEOUT'] = str(config.timeout)
        os.environ['DEFAULT_EMPLOYEE_TABLE'] = config.default_table

        # إعادة تهيئة الاتصال بقاعدة البيانات
        from app.database import DatabaseConnection
        global db
        db = DatabaseConnection()

        return {
            "detail": get_message("db_config_saved", lang) if lang == "ar" else "Database configuration saved successfully",
            "message": "تم حفظ إعدادات قاعدة البيانات بنجاح - Database configuration saved successfully",
            "config_path": config_path
        }

    except Exception as e:
        logger.error(f"خطأ في حفظ إعدادات قاعدة البيانات: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في حفظ الإعدادات - Error saving configuration: {str(e)}"
        )


@router.get("/database/load-config")
async def load_database_config(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    تحميل إعدادات قاعدة البيانات المحفوظة - Load saved database configuration

    Returns:
        إعدادات قاعدة البيانات - Database configuration
    """
    try:
        config_path = os.path.join("data", "db_config.json")

        if not os.path.exists(config_path):
            return {
                "detail": "لا توجد إعدادات محفوظة - No saved configuration",
                "config": None
            }

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # إخفاء كلمة المرور
        if 'password' in config:
            config['password'] = '***'

        return {
            "detail": "تم تحميل الإعدادات بنجاح - Configuration loaded successfully",
            "config": config
        }

    except Exception as e:
        logger.error(f"خطأ في تحميل إعدادات قاعدة البيانات: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في تحميل الإعدادات - Error loading configuration: {str(e)}"
        )
