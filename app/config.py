"""
تكوين النظام - System Configuration
يحتوي على جميع الإعدادات والمسارات المطلوبة للنظام
"""
import os
from pathlib import Path
from typing import List

# المسارات الأساسية - Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
POLICIES_DIR = BASE_DIR / "policies"
EMPLOYEES_DIR = DATA_DIR / "employees"

# إنشاء المجلدات المطلوبة - Create required directories
for p in (DATA_DIR, MODELS_DIR, LOGS_DIR, POLICIES_DIR, EMPLOYEES_DIR):
    p.mkdir(exist_ok=True, parents=True)

# مسارات النماذج - Model Paths
PROMOTION_MODEL_PATH = MODELS_DIR / "promotion_model.joblib"
PERFORMANCE_MODEL_PATH = MODELS_DIR / "performance_model.joblib"
METRICS_PATH = MODELS_DIR / "last_metrics.json"
MODEL_VERSION_PATH = MODELS_DIR / "model_version.json"

# مسارات السياسات - Policy Paths
POLICIES_DB_PATH = POLICIES_DIR / "policies.json"
POLICIES_EMBEDDINGS_PATH = POLICIES_DIR / "policy_embeddings.pkl"

# مسارات السجلات - Log Paths
LOG_FILE = LOGS_DIR / "hrml.log"

# إعدادات التعلم الآلي - ML Settings
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
N_ESTIMATORS = 300
MAX_DEPTH = None

# أعمدة البيانات - Data Columns
TARGET_COL = "promotion_eligible"

# الأعمدة الرقمية - Numerical Features
NUMERICAL_COLS = [
    "Age",  # العمر
    "Years_Since_Contract_Start",  # سنوات الخبرة
    "Salary_Total",  # الراتب الإجمالي
    "Basic_Salary",  # الراتب الأساسي
    "Allowances",  # البدلات
    "Insurance_Salary",  # راتب التأمين
    "Remaining_Contract_Renewal",  # المدة المتبقية للتجديد
    "Car_Ride_Time",  # وقت الانتقال
    "Skill_level_measurement_certificate",  # شهادة قياس المهارات
    "Training_Hours",  # ساعات التدريب
    "Performance_Score",  # درجة الأداء
    "Awards"  # الجوائز
]

# الأعمدة الفئوية - Categorical Features
CATEGORICAL_COLS = [
    "Dept_Name",  # القسم
    "Jop_Name",  # المسمى الوظيفي
    "Emp_Type",  # نوع الموظف
    "Working_Condition",  # حالة العمل
    "Emp_Marital_Status",  # الحالة الاجتماعية
    "Governorate",  # المحافظة
    "Shift_Type",  # نوع الوردية
    "gender"  # الجنس
]

# جميع الأعمدة المطلوبة - All Feature Columns
FEATURE_COLS = NUMERICAL_COLS + CATEGORICAL_COLS

# أعمدة تحليل الأداء - Performance Analysis Columns
PERFORMANCE_FEATURES = [
    "Performance_Score",
    "Training_Hours",
    "Awards",
    "Salary_Total",
    "Years_Since_Contract_Start"
]

# الأعمدة الأصلية من قاعدة البيانات - Original Database Columns
DB_COLUMNS = [
    "Emp_ID", "Emp_Full_Name", "Emp_Phone1", "Emp_Address", "Emp_Marital_Status",
    "Emp_Nationality", "People_With_Special_Needs", "National_ID", "Date_Birth",
    "Place_Birth", "Emp_Type", "Working_Condition", "Dept_Name", "Jop_Name",
    "Emp_Date_Hiring", "Emp_Car", "Car_Ride_Time", "Car_Pick_Up_Point",
    "Insurance_Status", "Jop_Code_insurance", "Jop_Name_insurance", "Health_Card",
    "Health_Card_Expiration_Date", "Number_Insurance", "Date_Insurance_Start",
    "Insurance_Salary", "Percentage_Insurance_Payable", "Due_Insurance_Amount",
    "Form_S1", "Confirmation_Insurance_Entry", "Delivery_Date_S1", "Receive_Date_S1",
    "Form_S6", "Delivery_Date_S6", "Receive_Date_S6", "Hiring_Date_Health_Card",
    "Skill_level_measurement_certificate", "End_date_probationary_period",
    "CurrentWeekShift", "NextWeekShift", "Friday_Operation", "Shift_Type",
    "Entrance_Date_S1", "Entrance_Number_S1", "Remaining_Contract_Renewal",
    "Medical_Exam_Form_Submission", "Years_Since_Contract_Start",
    "Contract_Renewal_Date", "Contract_Expiry_Date", "Insurance_Code",
    "Personal_ID_Expiry_Date", "Contract_Renewal_Month", "Military_Service_Certificate",
    "Qualification_Certificate", "Birth_Certificate", "Insurance_Printout",
    "ID_Card_Photo", "Personal_Photos", "Employment_Contract", "Medical_Exam_Form",
    "Criminal_Record_Check", "Social_Status_Report", "Work_Heel", "Heel_Work_Number",
    "Heel_Work_Registration_Date", "Heel_Work_Recipient", "Heel_Work_Recipient_Address",
    "Entrance_Number_S6", "Entrance_Date_S6", "Shift_paper", "Age", "Date_Resignation",
    "Reason_Resignation", "Mother_Name", "Confirm_Exit_Insurance", "Governorate",
    "Direct_Manager", "International_Subscription_Expiry_Date",
    "Orient_Subscription_Start_Date", "Orient_Incoming_Number", "Orient_Incoming_Date",
    "Orient_S1_Delivery_Date", "Orient_S1_Receipt_Date", "Orient_Insurance_Entry_Confirmation",
    "ElDawliya_S6", "Orient_S1", "Salary_Total", "Salary_Total_Text", "Basic_Salary",
    "Allowances"
]

# إعدادات اللغة - Language Settings
DEFAULT_LANGUAGE = "ar"  # Arabic by default
SUPPORTED_LANGUAGES = ["ar", "en"]

# إعدادات الأمان - Security Settings
MAX_FILE_SIZE_MB = 50

# امتدادات الملفات المدعومة للبيانات - Supported data file extensions
ALLOWED_DATA_EXTENSIONS = [
    ".csv", ".tsv",  # CSV and TSV files
    ".xlsx", ".xls", ".xlsb", ".xlsm",  # Excel files
    ".txt",  # Text files
    ".json",  # JSON files
    ".parquet",  # Parquet files
    ".feather"  # Feather files
]

# امتدادات ملفات السياسات - Policy file extensions
ALLOWED_POLICY_EXTENSIONS = [".pdf", ".docx", ".txt"]

# جميع الامتدادات المسموحة - All allowed extensions
ALLOWED_UPLOAD_EXTENSIONS = ALLOWED_DATA_EXTENSIONS + ALLOWED_POLICY_EXTENSIONS

# أنواع MIME المدعومة - Supported MIME types
ALLOWED_MIME_TYPES = [
    # CSV and TSV
    "text/csv",
    "text/tab-separated-values",
    "text/plain",
    # Excel files
    "application/vnd.ms-excel",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel.sheet.binary.macroEnabled.12",  # .xlsb
    "application/vnd.ms-excel.sheet.macroEnabled.12",  # .xlsm
    # JSON
    "application/json",
    # Parquet
    "application/octet-stream",  # Generic binary (for .parquet, .feather, .xlsb)
    "application/vnd.apache.parquet",
    # Policy files
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

# إعدادات النظام - System Settings
API_VERSION = "2.0.0"
API_TITLE = "نظام الموارد البشرية الذكي - Smart HR System"
API_DESCRIPTION = """
نظام متكامل للموارد البشرية يعتمد على الذكاء الاصطناعي
- التنبؤ بالترقيات
- تحليل الأداء
- إدارة السياسات
- التوصيات الذكية
- الامتثال للوائح
"""

# حدود التحقق - Validation Limits
MIN_AGE = 18
MAX_AGE = 70
MIN_YEARS_EXPERIENCE = 0
MAX_YEARS_EXPERIENCE = 50
MIN_SALARY = 0
MAX_SALARY = 1000000
MIN_TRAINING_HOURS = 0
MAX_TRAINING_HOURS = 2000
MIN_AWARDS = 0
MAX_AWARDS = 50
MIN_PERFORMANCE = 0
MAX_PERFORMANCE = 100
MIN_CAR_RIDE_TIME = 0
MAX_CAR_RIDE_TIME = 300  # دقائق
MIN_SKILL_LEVEL = 0
MAX_SKILL_LEVEL = 10
MIN_CONTRACT_RENEWAL = 0
MAX_CONTRACT_RENEWAL = 60  # شهور

# أنواع الموظفين - Employee Types
VALID_EMP_TYPES = [
    "دائم", "مؤقت", "متعاقد", "موسمي", "تدريب",
    "permanent", "temporary", "contract", "seasonal", "training"
]

# حالات العمل - Working Conditions
VALID_WORKING_CONDITIONS = [
    "عامل", "موظف", "إداري", "فني", "مشرف",
    "worker", "employee", "administrative", "technical", "supervisor"
]

# الحالات الاجتماعية - Marital Status
VALID_MARITAL_STATUS = [
    "أعزب", "متزوج", "مطلق", "أرمل",
    "single", "married", "divorced", "widowed"
]

# أنواع الورديات - Shift Types
VALID_SHIFT_TYPES = [
    "صباحي", "مسائي", "ليلي", "متغير", "ثابت",
    "morning", "evening", "night", "rotating", "fixed"
]

# الجنس - Gender Options
VALID_GENDERS = ["ذكر", "أنثى", "male", "female", "m", "f"]

# القيم الافتراضية للأعمدة المحسوبة - Default values for calculated columns
DEFAULT_TRAINING_HOURS = 0
DEFAULT_PERFORMANCE_SCORE = 50
DEFAULT_AWARDS = 0

# Backward compatibility
MODEL_PATH = PROMOTION_MODEL_PATH

# إعدادات قاعدة البيانات - Database Settings
SQL_SERVER_HOST = os.getenv("SQL_SERVER_HOST", "localhost")
SQL_SERVER_PORT = os.getenv("SQL_SERVER_PORT", "1433")
SQL_SERVER_DATABASE = os.getenv("SQL_SERVER_DATABASE", "HR_Database")
SQL_SERVER_USERNAME = os.getenv("SQL_SERVER_USERNAME", "sa")
SQL_SERVER_PASSWORD = os.getenv("SQL_SERVER_PASSWORD", "")
SQL_SERVER_DRIVER = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_SERVER_TIMEOUT = int(os.getenv("SQL_SERVER_TIMEOUT", "60"))

# جدول الموظفين الافتراضي - Default Employee Table
DEFAULT_EMPLOYEE_TABLE = os.getenv("DEFAULT_EMPLOYEE_TABLE", "Employees")

# استعلام SQL الافتراضي - Default SQL Query
DEFAULT_SQL_QUERY = f"SELECT * FROM {DEFAULT_EMPLOYEE_TABLE}"
