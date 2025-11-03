"""
أدوات معالجة البيانات - Data Processing Utilities
يحتوي على وظائف تنظيف ومعالجة البيانات
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from loguru import logger
from typing import Tuple, List, Optional
import joblib
import json
from pathlib import Path

from app.config import (
    NUMERICAL_COLS, CATEGORICAL_COLS, TARGET_COL,
    TEST_SIZE, RANDOM_STATE, FEATURE_COLS,
    VALID_GENDERS, DEFAULT_TRAINING_HOURS,
    DEFAULT_PERFORMANCE_SCORE, DEFAULT_AWARDS
)


def read_data_file(file_path: Path, file_extension: str = None) -> pd.DataFrame:
    """
    قراءة ملف بيانات من أي صيغة مدعومة - Read data file from any supported format

    Args:
        file_path: مسار الملف - File path
        file_extension: امتداد الملف (اختياري) - File extension (optional)

    Returns:
        البيانات كـ DataFrame - Data as DataFrame

    Raises:
        ValueError: إذا كانت الصيغة غير مدعومة - If format is not supported
        Exception: إذا فشلت قراءة الملف - If file reading fails
    """
    if file_extension is None:
        file_extension = file_path.suffix.lower()

    logger.info(f"قراءة ملف بصيغة: {file_extension}")

    try:
        # CSV files
        if file_extension == '.csv':
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"تم قراءة CSV بنجاح باستخدام ترميز: {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
            raise ValueError("فشل في قراءة ملف CSV بجميع الترميزات المدعومة")

        # TSV files
        elif file_extension == '.tsv':
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, sep='\t', encoding=encoding)
                    logger.info(f"تم قراءة TSV بنجاح باستخدام ترميز: {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
            raise ValueError("فشل في قراءة ملف TSV بجميع الترميزات المدعومة")

        # Excel files (.xlsx, .xlsm)
        elif file_extension in ['.xlsx', '.xlsm']:
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info(f"تم قراءة ملف Excel ({file_extension}) بنجاح")
            return df

        # Old Excel files (.xls)
        elif file_extension == '.xls':
            try:
                df = pd.read_excel(file_path, engine='xlrd')
                logger.info("تم قراءة ملف .xls بنجاح باستخدام xlrd")
                return df
            except Exception:
                # Fallback to openpyxl
                df = pd.read_excel(file_path, engine='openpyxl')
                logger.info("تم قراءة ملف .xls بنجاح باستخدام openpyxl")
                return df

        # Binary Excel files (.xlsb)
        elif file_extension == '.xlsb':
            try:
                import pyxlsb
                df = pd.read_excel(file_path, engine='pyxlsb')
                logger.info("تم قراءة ملف .xlsb بنجاح")
                return df
            except ImportError:
                raise ValueError("مكتبة pyxlsb غير مثبتة. يرجى تثبيتها لقراءة ملفات .xlsb")

        # JSON files
        elif file_extension == '.json':
            # Try different orientations
            for orient in ['records', 'index', 'columns', 'values']:
                try:
                    df = pd.read_json(file_path, orient=orient)
                    logger.info(f"تم قراءة JSON بنجاح باستخدام orientation: {orient}")
                    return df
                except:
                    continue
            # If all fail, try without orient
            df = pd.read_json(file_path)
            logger.info("تم قراءة JSON بنجاح")
            return df

        # Parquet files
        elif file_extension == '.parquet':
            try:
                df = pd.read_parquet(file_path, engine='pyarrow')
                logger.info("تم قراءة ملف Parquet بنجاح باستخدام pyarrow")
                return df
            except:
                df = pd.read_parquet(file_path, engine='fastparquet')
                logger.info("تم قراءة ملف Parquet بنجاح باستخدام fastparquet")
                return df

        # Feather files
        elif file_extension == '.feather':
            df = pd.read_feather(file_path)
            logger.info("تم قراءة ملف Feather بنجاح")
            return df

        # Text files (try as CSV)
        elif file_extension == '.txt':
            # Try as CSV first
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                logger.info("تم قراءة ملف TXT كـ CSV بنجاح")
                return df
            except:
                # Try with tab separator
                try:
                    df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                    logger.info("تم قراءة ملف TXT كـ TSV بنجاح")
                    return df
                except:
                    # Try with any whitespace
                    df = pd.read_csv(file_path, sep=r'\s+', encoding='utf-8')
                    logger.info("تم قراءة ملف TXT بنجاح")
                    return df

        else:
            raise ValueError(f"صيغة الملف غير مدعومة: {file_extension}")

    except Exception as e:
        logger.error(f"خطأ في قراءة الملف {file_path}: {str(e)}")
        raise


def prepare_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    تحضير بيانات الموظفين من قاعدة البيانات - Prepare employee data from database

    Args:
        df: البيانات الأولية من قاعدة البيانات - Raw dataframe from database

    Returns:
        البيانات المحضرة - Prepared dataframe
    """
    logger.info(f"بدء تحضير بيانات الموظفين. الصفوف الأولية: {len(df)}")

    # حساب العمر من تاريخ الميلاد إذا لم يكن موجوداً
    if 'Age' not in df.columns and 'Date_Birth' in df.columns:
        try:
            df['Date_Birth'] = pd.to_datetime(df['Date_Birth'], errors='coerce')
            df['Age'] = ((pd.Timestamp.now() - df['Date_Birth']).dt.days / 365.25).astype(int)
            logger.info("تم حساب العمر من تاريخ الميلاد")
        except Exception as e:
            logger.warning(f"فشل حساب العمر: {e}")
            df['Age'] = np.nan

    # حساب سنوات الخبرة من تاريخ التعيين إذا لم تكن موجودة
    if 'Years_Since_Contract_Start' not in df.columns and 'Emp_Date_Hiring' in df.columns:
        try:
            df['Emp_Date_Hiring'] = pd.to_datetime(df['Emp_Date_Hiring'], errors='coerce')
            df['Years_Since_Contract_Start'] = ((pd.Timestamp.now() - df['Emp_Date_Hiring']).dt.days / 365.25)
            logger.info("تم حساب سنوات الخبرة من تاريخ التعيين")
        except Exception as e:
            logger.warning(f"فشل حساب سنوات الخبرة: {e}")
            df['Years_Since_Contract_Start'] = np.nan

    # إنشاء أعمدة محسوبة إذا لم تكن موجودة
    if 'Training_Hours' not in df.columns:
        df['Training_Hours'] = 0  # سيتم تحديثه لاحقاً من بيانات التدريب
        logger.info("تم إنشاء عمود Training_Hours بقيمة افتراضية")

    if 'Performance_Score' not in df.columns:
        df['Performance_Score'] = 50  # قيمة افتراضية متوسطة
        logger.info("تم إنشاء عمود Performance_Score بقيمة افتراضية")

    if 'Awards' not in df.columns:
        df['Awards'] = 0  # قيمة افتراضية
        logger.info("تم إنشاء عمود Awards بقيمة افتراضية")

    # توحيد عمود الجنس
    if 'gender' not in df.columns:
        # محاولة استخراج الجنس من الاسم أو البيانات الأخرى
        df['gender'] = 'unknown'
        logger.info("تم إنشاء عمود gender بقيمة افتراضية")

    logger.info(f"اكتمل تحضير البيانات. الصفوف النهائية: {len(df)}")
    return df


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    تنظيف البيانات - Clean dataset

    Args:
        df: البيانات الأولية - Raw dataframe

    Returns:
        البيانات المنظفة - Cleaned dataframe
    """
    logger.info(f"بدء تنظيف البيانات. الصفوف الأولية: {len(df)}")

    # إزالة المكررات - Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        logger.info(f"تم إزالة {duplicates_removed} صف مكرر")

    # تنظيف الأعمدة الرقمية - Clean numerical columns
    for col in NUMERICAL_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # إزالة القيم السالبة غير المنطقية - Remove illogical negative values
            negative_cols = ['Age', 'Years_Since_Contract_Start', 'Salary_Total',
                           'Basic_Salary', 'Allowances', 'Insurance_Salary',
                           'Training_Hours', 'Awards', 'Car_Ride_Time']
            if col in negative_cols:
                df.loc[df[col] < 0, col] = np.nan

    # تنظيف الأعمدة الفئوية - Clean categorical columns
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # استبدال القيم الفارغة - Replace empty values
            df[col] = df[col].replace(['', 'nan', 'none', 'null', 'None'], np.nan)

    # توحيد قيم الجنس - Normalize gender values
    if 'gender' in df.columns:
        gender_mapping = {
            'ذكر': 'male', 'انثى': 'female', 'أنثى': 'female',
            'm': 'male', 'f': 'female', 'ذ': 'male', 'أ': 'female'
        }
        df['gender'] = df['gender'].str.lower().replace(gender_mapping)
        # التحقق من القيم الصالحة
        valid_genders_normalized = ['male', 'female']
        invalid_genders = ~df['gender'].isin(valid_genders_normalized + [np.nan])
        if invalid_genders.any():
            logger.warning(f"تم العثور على {invalid_genders.sum()} قيمة جنس غير صالحة")
            df.loc[invalid_genders, 'gender'] = np.nan

    logger.info(f"اكتمل تنظيف البيانات. الصفوف النهائية: {len(df)}")
    return df


def create_promotion_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    إنشاء عمود الهدف (promotion_eligible) بناءً على معايير محددة
    Create target column (promotion_eligible) based on specific criteria

    Args:
        df: البيانات - Dataframe

    Returns:
        البيانات مع عمود الهدف - Dataframe with target column
    """
    logger.info("إنشاء عمود الهدف (promotion_eligible)...")

    # المعايير الأساسية للترقية:
    # 1. سنوات الخبرة >= 2
    # 2. الراتب الإجمالي > متوسط الراتب
    # 3. درجة الأداء >= 70
    # 4. ساعات التدريب >= 20

    conditions = []

    # معيار سنوات الخبرة
    if 'Years_Since_Contract_Start' in df.columns:
        conditions.append(df['Years_Since_Contract_Start'] >= 2)

    # معيار الراتب
    if 'Salary_Total' in df.columns:
        median_salary = df['Salary_Total'].median()
        conditions.append(df['Salary_Total'] > median_salary)

    # معيار الأداء
    if 'Performance_Score' in df.columns:
        conditions.append(df['Performance_Score'] >= 70)

    # معيار التدريب
    if 'Training_Hours' in df.columns:
        conditions.append(df['Training_Hours'] >= 20)

    # معيار الجوائز
    if 'Awards' in df.columns:
        conditions.append(df['Awards'] >= 1)

    # حساب عدد المعايير المحققة
    if conditions:
        # الموظف مؤهل للترقية إذا حقق 60% من المعايير على الأقل
        total_conditions = len(conditions)
        required_conditions = int(total_conditions * 0.6)

        # حساب عدد المعايير المحققة لكل موظف
        conditions_met = sum(conditions)
        df['promotion_eligible'] = (conditions_met >= required_conditions).astype(int)

        eligible_count = df['promotion_eligible'].sum()
        logger.info(f"تم إنشاء عمود الهدف: {eligible_count} موظف مؤهل للترقية من أصل {len(df)}")
    else:
        # إذا لم تتوفر معايير، استخدم قيمة افتراضية
        df['promotion_eligible'] = 0
        logger.warning("لم يتم العثور على معايير كافية، تم استخدام قيمة افتراضية")

    return df


def validate_dataframe(df: pd.DataFrame, require_target: bool = True) -> Tuple[bool, List[str]]:
    """
    التحقق من صحة البيانات - Validate dataframe

    Args:
        df: البيانات - Dataframe
        require_target: هل يتطلب عمود الهدف - Whether target column is required

    Returns:
        (صالح، قائمة الأخطاء) - (is_valid, list of errors)
    """
    errors = []

    # التحقق من وجود الأعمدة المطلوبة - Check required columns
    required_cols = FEATURE_COLS + CATEGORICAL_COLS
    if require_target:
        required_cols = required_cols + [TARGET_COL]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"الأعمدة المفقودة: {', '.join(missing_cols)}")

    # التحقق من عدم وجود صفوف - Check for empty dataframe
    if len(df) == 0:
        errors.append("البيانات فارغة")

    # التحقق من نسبة القيم المفقودة - Check missing values ratio
    for col in df.columns:
        missing_ratio = df[col].isna().sum() / len(df)
        if missing_ratio > 0.5:
            errors.append(f"العمود '{col}' يحتوي على أكثر من 50% قيم مفقودة")

    is_valid = len(errors) == 0
    return is_valid, errors


def build_preprocessor() -> ColumnTransformer:
    """
    بناء معالج البيانات - Build data preprocessor

    Returns:
        معالج البيانات - Data preprocessor
    """
    # معالج الأعمدة الرقمية - Numerical pipeline
    num_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # معالج الأعمدة الفئوية - Categorical pipeline
    cat_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # دمج المعالجات - Combine preprocessors
    prep = ColumnTransformer(
        transformers=[
            ("num", num_pipe, NUMERICAL_COLS),
            ("cat", cat_pipe, CATEGORICAL_COLS)
        ],
        remainder='drop'
    )

    return prep


def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    تقسيم البيانات - Split data into train and test sets

    Args:
        df: البيانات - Dataframe

    Returns:
        (X_train, X_test, y_train, y_test)

    Raises:
        ValueError: إذا لم يوجد عمود الهدف - If target column not found
    """
    if TARGET_COL not in df.columns:
        raise ValueError(f"عمود الهدف '{TARGET_COL}' غير موجود في البيانات")

    # استخراج المتغيرات والهدف - Extract features and target
    X = df[FEATURE_COLS + CATEGORICAL_COLS].copy()
    y = df[TARGET_COL].copy()

    # التحقق من وجود فئات كافية - Check for sufficient classes
    if y.nunique() < 2:
        logger.warning("البيانات تحتوي على فئة واحدة فقط")
        stratify = None
    else:
        stratify = y

    # تقسيم البيانات - Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify
    )

    logger.info(f"تم تقسيم البيانات: تدريب={len(X_train)}, اختبار={len(X_test)}")

    return X_train, X_test, y_train, y_test


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    الحصول على ملخص البيانات - Get data summary

    Args:
        df: البيانات - Dataframe

    Returns:
        ملخص البيانات - Data summary
    """
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "missing_values": df.isna().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
    }

    # إحصائيات الأعمدة الرقمية - Numerical columns statistics
    if NUMERICAL_COLS:
        num_cols_present = [col for col in NUMERICAL_COLS if col in df.columns]
        if num_cols_present:
            summary["numerical_stats"] = df[num_cols_present].describe().to_dict()

    # إحصائيات الأعمدة الفئوية - Categorical columns statistics
    if CATEGORICAL_COLS:
        cat_cols_present = [col for col in CATEGORICAL_COLS if col in df.columns]
        if cat_cols_present:
            summary["categorical_stats"] = {
                col: df[col].value_counts().to_dict()
                for col in cat_cols_present
            }

    return summary

