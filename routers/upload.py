"""
موجه رفع الملفات - Upload Router
يوفر نقاط نهاية لرفع البيانات والملفات
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from typing import Optional
import pandas as pd
import numpy as np
import shutil
import os
from loguru import logger

from app.config import (
    DATA_DIR, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_MB, ALLOWED_DATA_EXTENSIONS
)
from app.data_utils import clean_df, validate_dataframe, get_data_summary, read_data_file
from app.i18n import get_message
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["رفع الملفات - Upload"])


def safe_json_convert(df: pd.DataFrame) -> list:
    """
    تحويل DataFrame إلى قائمة قواميس بشكل آمن للـ JSON
    Convert DataFrame to list of dicts safely for JSON

    Args:
        df: DataFrame to convert

    Returns:
        List of dictionaries with JSON-safe values
    """
    # استبدال NaN و Infinity بـ None
    df_clean = df.replace([np.inf, -np.inf], np.nan)

    # تحويل إلى قواميس
    records = df_clean.to_dict(orient="records")

    # استبدال NaN بـ None في كل سجل
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, (np.integer, np.floating)):
                # تحويل أنواع numpy إلى أنواع Python الأساسية
                record[key] = value.item()

    return records


def clean_summary_for_json(summary: dict) -> dict:
    """
    تنظيف الملخص من القيم غير الصالحة للـ JSON
    Clean summary from JSON-invalid values

    Args:
        summary: Dictionary containing summary data

    Returns:
        Cleaned dictionary safe for JSON serialization
    """
    def clean_value(value):
        """تنظيف قيمة واحدة"""
        if isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(v) for v in value]
        elif pd.isna(value):
            return None
        elif isinstance(value, (np.integer, np.floating)):
            if np.isinf(value):
                return None
            return value.item()
        elif isinstance(value, (float, int)):
            if np.isinf(value) or np.isnan(value):
                return None
            return value
        else:
            return value

    return clean_value(summary)


@router.post("/dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    رفع مجموعة بيانات للتدريب - Upload dataset for training

    Args:
        file: ملف بيانات (CSV, Excel, JSON, Parquet, إلخ) - Data file (CSV, Excel, JSON, Parquet, etc.)
        lang: اللغة - Language

    Returns:
        معلومات الملف المرفوع - Uploaded file information

    Supported formats:
        - CSV: .csv, .tsv
        - Excel: .xlsx, .xls, .xlsb, .xlsm
        - Text: .txt
        - JSON: .json
        - Parquet: .parquet
        - Feather: .feather
    """
    try:
        # استخراج امتداد الملف - Extract file extension
        file_extension = Path(file.filename).suffix.lower()

        # التحقق من امتداد الملف - Validate file extension
        if file_extension not in ALLOWED_DATA_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=get_message("file_invalid_type", lang) +
                       f"\n\nالصيغ المدعومة - Supported formats: {', '.join(ALLOWED_DATA_EXTENSIONS)}"
            )

        # التحقق من حجم الملف - Validate file size
        file.file.seek(0, 2)  # الانتقال إلى نهاية الملف - Seek to end
        file_size = file.file.tell()  # الحصول على الحجم - Get size
        file.file.seek(0)  # العودة إلى البداية - Return to start

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=get_message("file_too_large", lang, max_size=MAX_FILE_SIZE_MB)
            )

        # حفظ الملف بامتداده الأصلي - Save file with original extension
        saved_path = DATA_DIR / f"raw_dataset{file_extension}"

        # حفظ الملف - Save file
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"تم حفظ الملف: {saved_path} (الحجم: {file_size / 1024:.2f} KB)")

        # قراءة البيانات باستخدام الدالة الجديدة - Read data using new function
        try:
            df = read_data_file(saved_path, file_extension)
            logger.info(f"تم قراءة البيانات بنجاح: {len(df)} صف، {len(df.columns)} عمود")
        except Exception as e:
            logger.error(f"فشل في قراءة الملف: {e}")
            raise HTTPException(
                status_code=422,
                detail=get_message("file_parse_error", lang, error=str(e))
            )

        # التحقق من البيانات - Validate data
        if df.empty:
            raise HTTPException(
                status_code=422,
                detail=get_message("file_empty", lang)
            )

        # تنظيف البيانات - Clean data
        df = clean_df(df)

        # التحقق من صحة البيانات - Validate dataframe
        is_valid, errors = validate_dataframe(df, require_target=True)
        if not is_valid:
            logger.warning(f"مشاكل في البيانات: {errors}")
            # لا نرفض الملف، فقط نحذر - Don't reject, just warn

        # حفظ البيانات المنظفة - Save cleaned data
        cleaned_path = DATA_DIR / "cleaned_dataset.csv"
        df.to_csv(cleaned_path, index=False, encoding='utf-8')

        logger.info(f"تم تنظيف وحفظ البيانات: {cleaned_path}")

        # الحصول على ملخص البيانات - Get data summary
        try:
            summary = get_data_summary(df)
            # تنظيف القيم غير الصالحة في الملخص
            summary = clean_summary_for_json(summary)
        except Exception as e:
            logger.warning(f"فشل في إنشاء الملخص: {e}")
            summary = {}

        return {
            "status": "success",
            "detail": get_message("file_uploaded", lang),
            "message": get_message("dataset_cleaned", lang),
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "shape": list(df.shape),
            "column_names": list(df.columns),
            "preview": safe_json_convert(df.head(5)),
            "summary": summary,
            "validation_warnings": errors if not is_valid else []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ غير متوقع في رفع الملف: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )
