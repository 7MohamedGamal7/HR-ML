"""
نظام الترجمة والدعم متعدد اللغات - Internationalization Module
يوفر الدعم الكامل للغة العربية والإنجليزية
"""

from typing import Dict, Any
from app.config import DEFAULT_LANGUAGE

# الرسائل باللغة العربية - Arabic Messages
MESSAGES_AR = {
    # رسائل عامة - General Messages
    "system_running": "نظام الموارد البشرية الذكي يعمل بنجاح. قم بزيارة /docs للحصول على واجهة Swagger.",
    "system_healthy": "النظام يعمل بشكل صحيح",
    "success": "تمت العملية بنجاح",
    "error": "حدث خطأ",
    
    # رسائل رفع الملفات - Upload Messages
    "file_uploaded": "تم رفع الملف بنجاح",
    "file_invalid_type": "نوع الملف غير صالح. الصيغ المدعومة: CSV, TSV, Excel (.xlsx, .xls, .xlsb, .xlsm), JSON, Parquet, Feather, TXT",
    "file_too_large": "حجم الملف كبير جداً. الحد الأقصى هو {max_size} ميجابايت",
    "file_parse_error": "فشل في قراءة الملف: {error}",
    "file_empty": "الملف فارغ",
    "file_corrupted": "الملف تالف أو غير قابل للقراءة",
    "file_format_unsupported": "صيغة الملف غير مدعومة: {format}",
    "dataset_cleaned": "تم تنظيف البيانات بنجاح",
    "rows_processed": "تم معالجة {count} صف",
    
    # رسائل التدريب - Training Messages
    "training_started": "بدأ تدريب النموذج...",
    "training_completed": "اكتمل تدريب النموذج بنجاح",
    "model_saved": "تم حفظ النموذج بنجاح",
    "no_dataset": "لا يوجد مجموعة بيانات. يرجى رفع البيانات أولاً عبر /upload/dataset",
    "dataset_empty": "مجموعة البيانات فارغة",
    "training_error": "حدث خطأ أثناء التدريب: {error}",
    
    # رسائل التنبؤ - Prediction Messages
    "prediction_success": "تم التنبؤ بنجاح",
    "model_not_found": "النموذج غير موجود. يرجى تدريب النموذج أولاً عبر /train",
    "prediction_error": "حدث خطأ أثناء التنبؤ: {error}",
    "promotion_eligible": "مؤهل للترقية",
    "promotion_not_eligible": "غير مؤهل للترقية",
    "probability": "الاحتمالية",
    "confidence": "مستوى الثقة",
    
    # رسائل السياسات - Policy Messages
    "policy_uploaded": "تم رفع السياسة بنجاح",
    "policy_not_found": "السياسة غير موجودة",
    "policy_deleted": "تم حذف السياسة بنجاح",
    "policy_updated": "تم تحديث السياسة بنجاح",
    "policies_retrieved": "تم استرجاع السياسات بنجاح",
    "policy_query_success": "تم البحث في السياسات بنجاح",
    
    # رسائل الموظفين - Employee Messages
    "employee_added": "تم إضافة الموظف بنجاح",
    "employee_updated": "تم تحديث بيانات الموظف بنجاح",
    "employee_deleted": "تم حذف الموظف بنجاح",
    "employee_not_found": "الموظف غير موجود",
    "employee_exists": "الموظف موجود بالفعل",
    
    # رسائل تحليل الأداء - Performance Analysis Messages
    "performance_analyzed": "تم تحليل الأداء بنجاح",
    "performance_excellent": "أداء ممتاز",
    "performance_good": "أداء جيد",
    "performance_average": "أداء متوسط",
    "performance_below_average": "أداء أقل من المتوسط",
    "performance_poor": "أداء ضعيف",
    
    # رسائل التوصيات - Recommendation Messages
    "recommendations_generated": "تم إنشاء التوصيات بنجاح",
    "no_recommendations": "لا توجد توصيات متاحة",
    
    # رسائل الامتثال - Compliance Messages
    "compliance_check_passed": "اجتاز فحص الامتثال",
    "compliance_check_failed": "فشل في فحص الامتثال",
    "compliance_issues_found": "تم العثور على {count} مشكلة في الامتثال",
    
    # رسائل التحقق - Validation Messages
    "invalid_input": "بيانات الإدخال غير صالحة",
    "missing_field": "الحقل {field} مطلوب",
    "invalid_range": "القيمة يجب أن تكون بين {min} و {max}",

    # رسائل قاعدة البيانات - Database Messages
    "db_connection_success": "تم الاتصال بقاعدة البيانات بنجاح",
    "db_connection_failed": "فشل الاتصال بقاعدة البيانات: {error}",
    "db_query_success": "تم تنفيذ الاستعلام بنجاح",
    "db_query_failed": "فشل تنفيذ الاستعلام: {error}",
    "db_table_not_found": "الجدول {table} غير موجود",
    "db_data_loaded": "تم تحميل {count} صف من قاعدة البيانات",
    "db_training_started": "بدأ التدريب من قاعدة البيانات...",
    "db_training_success": "تم التدريب بنجاح من قاعدة البيانات",

    # ترجمات الأعمدة - Column Translations
    "col_age": "العمر",
    "col_years_experience": "سنوات الخبرة",
    "col_salary_total": "الراتب الإجمالي",
    "col_basic_salary": "الراتب الأساسي",
    "col_allowances": "البدلات",
    "col_insurance_salary": "راتب التأمين",
    "col_contract_renewal": "المدة المتبقية للتجديد",
    "col_car_ride_time": "وقت الانتقال",
    "col_skill_level": "مستوى المهارة",
    "col_training_hours": "ساعات التدريب",
    "col_performance_score": "درجة الأداء",
    "col_awards": "الجوائز",
    "col_dept_name": "القسم",
    "col_job_name": "المسمى الوظيفي",
    "col_emp_type": "نوع الموظف",
    "col_working_condition": "حالة العمل",
    "col_marital_status": "الحالة الاجتماعية",
    "col_governorate": "المحافظة",
    "col_shift_type": "نوع الوردية",
    "col_gender": "الجنس",
    "invalid_department": "القسم غير صالح",
    "invalid_gender": "الجنس غير صالح",
    
    # رسائل المقاييس - Metrics Messages
    "accuracy": "الدقة",
    "precision": "الدقة الموجبة",
    "recall": "الاستدعاء",
    "f1_score": "درجة F1",
    
    # حقول البيانات - Data Fields
    "experience": "سنوات الخبرة",
    "education_level": "المستوى التعليمي",
    "performance_score": "درجة الأداء",
    "training_hours": "ساعات التدريب",
    "awards": "الجوائز",
    "avg_work_hours": "متوسط ساعات العمل",
    "department": "القسم",
    "gender": "الجنس",
    "employee_id": "رقم الموظف",
    "name": "الاسم",
    
    # الأقسام - Departments
    "dept_hr": "الموارد البشرية",
    "dept_it": "تقنية المعلومات",
    "dept_finance": "المالية",
    "dept_sales": "المبيعات",
    "dept_marketing": "التسويق",
    "dept_operations": "العمليات",
    "dept_legal": "الشؤون القانونية",
    "dept_admin": "الإدارة",
    "dept_engineering": "الهندسة",
    "dept_support": "الدعم الفني",
}

# الرسائل باللغة الإنجليزية - English Messages
MESSAGES_EN = {
    # General Messages
    "system_running": "Smart HR System is running. Visit /docs for Swagger UI.",
    "system_healthy": "System is healthy",
    "success": "Operation completed successfully",
    "error": "An error occurred",
    
    # Upload Messages
    "file_uploaded": "File uploaded successfully",
    "file_invalid_type": "Invalid file type. Supported formats: CSV, TSV, Excel (.xlsx, .xls, .xlsb, .xlsm), JSON, Parquet, Feather, TXT",
    "file_too_large": "File is too large. Maximum size is {max_size} MB",
    "file_parse_error": "Failed to parse file: {error}",
    "file_empty": "File is empty",
    "file_corrupted": "File is corrupted or unreadable",
    "file_format_unsupported": "Unsupported file format: {format}",
    "dataset_cleaned": "Dataset cleaned successfully",
    "rows_processed": "Processed {count} rows",
    
    # Training Messages
    "training_started": "Model training started...",
    "training_completed": "Model training completed successfully",
    "model_saved": "Model saved successfully",
    "no_dataset": "No dataset found. Please upload data first via /upload/dataset",
    "dataset_empty": "Dataset is empty",
    "training_error": "Error during training: {error}",
    
    # Prediction Messages
    "prediction_success": "Prediction successful",
    "model_not_found": "Model not found. Please train the model first via /train",
    "prediction_error": "Error during prediction: {error}",
    "promotion_eligible": "Eligible for promotion",
    "promotion_not_eligible": "Not eligible for promotion",
    "probability": "Probability",
    "confidence": "Confidence",
    
    # Policy Messages
    "policy_uploaded": "Policy uploaded successfully",
    "policy_not_found": "Policy not found",
    "policy_deleted": "Policy deleted successfully",
    "policy_updated": "Policy updated successfully",
    "policies_retrieved": "Policies retrieved successfully",
    "policy_query_success": "Policy search completed successfully",
    
    # Employee Messages
    "employee_added": "Employee added successfully",
    "employee_updated": "Employee updated successfully",
    "employee_deleted": "Employee deleted successfully",
    "employee_not_found": "Employee not found",
    "employee_exists": "Employee already exists",
    
    # Performance Analysis Messages
    "performance_analyzed": "Performance analyzed successfully",
    "performance_excellent": "Excellent performance",
    "performance_good": "Good performance",
    "performance_average": "Average performance",
    "performance_below_average": "Below average performance",
    "performance_poor": "Poor performance",
    
    # Recommendation Messages
    "recommendations_generated": "Recommendations generated successfully",
    "no_recommendations": "No recommendations available",
    
    # Compliance Messages
    "compliance_check_passed": "Compliance check passed",
    "compliance_check_failed": "Compliance check failed",
    "compliance_issues_found": "Found {count} compliance issues",
    
    # Validation Messages
    "invalid_input": "Invalid input data",
    "missing_field": "Field {field} is required",
    "invalid_range": "Value must be between {min} and {max}",
    "invalid_department": "Invalid department",
    "invalid_gender": "Invalid gender",

    # Database Messages
    "db_connection_success": "Database connection successful",
    "db_connection_failed": "Database connection failed: {error}",
    "db_query_success": "Query executed successfully",
    "db_query_failed": "Query execution failed: {error}",
    "db_table_not_found": "Table {table} not found",
    "db_data_loaded": "Loaded {count} rows from database",
    "db_training_started": "Training from database started...",
    "db_training_success": "Training from database completed successfully",

    # Column Translations
    "col_age": "Age",
    "col_years_experience": "Years of Experience",
    "col_salary_total": "Total Salary",
    "col_basic_salary": "Basic Salary",
    "col_allowances": "Allowances",
    "col_insurance_salary": "Insurance Salary",
    "col_contract_renewal": "Remaining Contract Renewal",
    "col_car_ride_time": "Car Ride Time",
    "col_skill_level": "Skill Level",
    "col_training_hours": "Training Hours",
    "col_performance_score": "Performance Score",
    "col_awards": "Awards",
    "col_dept_name": "Department Name",
    "col_job_name": "Job Title",
    "col_emp_type": "Employee Type",
    "col_working_condition": "Working Condition",
    "col_marital_status": "Marital Status",
    "col_governorate": "Governorate",
    "col_shift_type": "Shift Type",
    "col_gender": "Gender",
    
    # Metrics Messages
    "accuracy": "Accuracy",
    "precision": "Precision",
    "recall": "Recall",
    "f1_score": "F1 Score",
    
    # Data Fields
    "experience": "Years of Experience",
    "education_level": "Education Level",
    "performance_score": "Performance Score",
    "training_hours": "Training Hours",
    "awards": "Awards",
    "avg_work_hours": "Average Work Hours",
    "department": "Department",
    "gender": "Gender",
    "employee_id": "Employee ID",
    "name": "Name",
    
    # Departments
    "dept_hr": "Human Resources",
    "dept_it": "Information Technology",
    "dept_finance": "Finance",
    "dept_sales": "Sales",
    "dept_marketing": "Marketing",
    "dept_operations": "Operations",
    "dept_legal": "Legal",
    "dept_admin": "Administration",
    "dept_engineering": "Engineering",
    "dept_support": "Support",
}

# قاموس اللغات - Languages Dictionary
MESSAGES = {
    "ar": MESSAGES_AR,
    "en": MESSAGES_EN
}


def get_message(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    الحصول على رسالة مترجمة - Get translated message
    
    Args:
        key: مفتاح الرسالة - Message key
        lang: اللغة (ar أو en) - Language (ar or en)
        **kwargs: متغيرات للتنسيق - Variables for formatting
    
    Returns:
        الرسالة المترجمة - Translated message
    """
    messages = MESSAGES.get(lang, MESSAGES_AR)
    message = messages.get(key, key)
    
    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError:
            pass
    
    return message


def translate_dict(data: Dict[str, Any], lang: str = DEFAULT_LANGUAGE) -> Dict[str, Any]:
    """
    ترجمة قاموس البيانات - Translate data dictionary
    
    Args:
        data: البيانات المراد ترجمتها - Data to translate
        lang: اللغة - Language
    
    Returns:
        البيانات المترجمة - Translated data
    """
    translated = {}
    for key, value in data.items():
        translated_key = get_message(key, lang)
        if isinstance(value, dict):
            translated[translated_key] = translate_dict(value, lang)
        elif isinstance(value, list):
            translated[translated_key] = [
                translate_dict(item, lang) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            translated[translated_key] = value
    return translated

