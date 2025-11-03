"""
موجه التنبؤ - Prediction Router
يوفر نقاط نهاية للتنبؤ بالترقيات
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import pandas as pd
from loguru import logger

from app.model_utils import load_model
from app.config import (
    MIN_AGE, MAX_AGE,
    MIN_YEARS_EXPERIENCE, MAX_YEARS_EXPERIENCE,
    MIN_SALARY, MAX_SALARY,
    MIN_PERFORMANCE, MAX_PERFORMANCE,
    MIN_TRAINING_HOURS, MAX_TRAINING_HOURS,
    MIN_AWARDS, MAX_AWARDS,
    MIN_CAR_RIDE_TIME, MAX_CAR_RIDE_TIME,
    MIN_SKILL_LEVEL, MAX_SKILL_LEVEL,
    MIN_CONTRACT_RENEWAL, MAX_CONTRACT_RENEWAL,
    VALID_EMP_TYPES, VALID_WORKING_CONDITIONS,
    VALID_MARITAL_STATUS, VALID_SHIFT_TYPES,
    VALID_GENDERS
)
from app.i18n import get_message

router = APIRouter(prefix="/predict", tags=["التنبؤ - Prediction"])


class Employee(BaseModel):
    """نموذج بيانات الموظف - Employee data model"""

    # الأعمدة الرقمية - Numerical Fields
    Age: int = Field(
        ...,
        ge=MIN_AGE,
        le=MAX_AGE,
        description="العمر - Age"
    )
    Years_Since_Contract_Start: float = Field(
        ...,
        ge=MIN_YEARS_EXPERIENCE,
        le=MAX_YEARS_EXPERIENCE,
        description="سنوات الخبرة - Years of experience"
    )
    Salary_Total: float = Field(
        ...,
        ge=MIN_SALARY,
        le=MAX_SALARY,
        description="الراتب الإجمالي - Total salary"
    )
    Basic_Salary: float = Field(
        ...,
        ge=MIN_SALARY,
        le=MAX_SALARY,
        description="الراتب الأساسي - Basic salary"
    )
    Allowances: float = Field(
        default=0,
        ge=0,
        le=MAX_SALARY,
        description="البدلات - Allowances"
    )
    Insurance_Salary: float = Field(
        default=0,
        ge=0,
        le=MAX_SALARY,
        description="راتب التأمين - Insurance salary"
    )
    Remaining_Contract_Renewal: int = Field(
        default=12,
        ge=MIN_CONTRACT_RENEWAL,
        le=MAX_CONTRACT_RENEWAL,
        description="المدة المتبقية للتجديد (شهور) - Remaining contract renewal (months)"
    )
    Car_Ride_Time: int = Field(
        default=0,
        ge=MIN_CAR_RIDE_TIME,
        le=MAX_CAR_RIDE_TIME,
        description="وقت الانتقال (دقائق) - Car ride time (minutes)"
    )
    Skill_level_measurement_certificate: int = Field(
        default=0,
        ge=MIN_SKILL_LEVEL,
        le=MAX_SKILL_LEVEL,
        description="شهادة قياس المهارات - Skill level certificate"
    )
    Training_Hours: float = Field(
        default=0,
        ge=MIN_TRAINING_HOURS,
        le=MAX_TRAINING_HOURS,
        description="ساعات التدريب - Training hours"
    )
    Performance_Score: float = Field(
        default=50,
        ge=MIN_PERFORMANCE,
        le=MAX_PERFORMANCE,
        description="درجة الأداء - Performance score (0-100)"
    )
    Awards: int = Field(
        default=0,
        ge=MIN_AWARDS,
        le=MAX_AWARDS,
        description="عدد الجوائز - Number of awards"
    )

    # الأعمدة الفئوية - Categorical Fields
    Dept_Name: str = Field(
        ...,
        description="القسم - Department name"
    )
    Jop_Name: str = Field(
        ...,
        description="المسمى الوظيفي - Job title"
    )
    Emp_Type: str = Field(
        ...,
        description="نوع الموظف - Employee type"
    )
    Working_Condition: str = Field(
        ...,
        description="حالة العمل - Working condition"
    )
    Emp_Marital_Status: str = Field(
        ...,
        description="الحالة الاجتماعية - Marital status"
    )
    Governorate: str = Field(
        ...,
        description="المحافظة - Governorate"
    )
    Shift_Type: str = Field(
        default="ثابت",
        description="نوع الوردية - Shift type"
    )
    gender: str = Field(
        ...,
        description="الجنس - Gender"
    )

    @validator('gender')
    def validate_gender(cls, v):
        """التحقق من صحة الجنس - Validate gender"""
        v_lower = v.lower()
        if v_lower not in VALID_GENDERS:
            raise ValueError(f"الجنس يجب أن يكون أحد: {', '.join(VALID_GENDERS)}")
        # توحيد القيمة
        if v_lower in ['ذكر', 'm', 'ذ']:
            return 'male'
        elif v_lower in ['أنثى', 'انثى', 'f', 'أ']:
            return 'female'
        return v_lower

    class Config:
        json_schema_extra = {
            "example": {
                "Age": 35,
                "Years_Since_Contract_Start": 5.0,
                "Salary_Total": 8000.0,
                "Basic_Salary": 6000.0,
                "Allowances": 2000.0,
                "Insurance_Salary": 6000.0,
                "Remaining_Contract_Renewal": 12,
                "Car_Ride_Time": 30,
                "Skill_level_measurement_certificate": 7,
                "Training_Hours": 40.0,
                "Performance_Score": 85.0,
                "Awards": 2,
                "Dept_Name": "تكنولوجيا المعلومات",
                "Jop_Name": "مبرمج",
                "Emp_Type": "دائم",
                "Working_Condition": "موظف",
                "Emp_Marital_Status": "متزوج",
                "Governorate": "القاهرة",
                "Shift_Type": "صباحي",
                "gender": "male"
            }
        }


class BatchPredictionRequest(BaseModel):
    """طلب تنبؤ جماعي - Batch prediction request"""
    employees: List[Employee]


@router.post("/")
async def predict_promotion(
    emp: Employee,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    التنبؤ بأهلية الترقية لموظف واحد - Predict promotion eligibility for single employee

    Args:
        emp: بيانات الموظف - Employee data
        lang: اللغة - Language

    Returns:
        نتيجة التنبؤ - Prediction result
    """
    try:
        # تحميل النموذج - Load model
        try:
            model = load_model()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail=get_message("model_not_found", lang)
            )

        # تحضير البيانات - Prepare data
        df = pd.DataFrame([emp.model_dump()])

        # التنبؤ - Make prediction
        pred = model.predict(df)[0]
        proba = model.predict_proba(df)[0].tolist()

        # تحديد مستوى الثقة - Determine confidence level
        confidence = max(proba)
        confidence_level = "عالية" if confidence > 0.8 else "متوسطة" if confidence > 0.6 else "منخفضة"

        logger.info(f"تنبؤ للموظف: {emp.model_dump()} => {pred} (ثقة: {confidence:.2f})")

        # إنشاء الاستجابة - Create response
        result = {
            "prediction": get_message("promotion_eligible", lang) if pred == 1 else get_message("promotion_not_eligible", lang),
            "promotion_eligible": bool(pred),
            "probability": {
                "no": round(proba[0], 4),
                "yes": round(proba[1], 4)
            },
            "confidence": round(confidence, 4),
            "confidence_level": confidence_level,
            "recommendation": _generate_recommendation(emp, pred, proba, lang)
        }

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=get_message("invalid_input", lang) + f": {str(e)}"
        )
    except Exception as e:
        logger.error(f"خطأ في التنبؤ: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("prediction_error", lang, error=str(e))
        )


@router.post("/batch")
async def predict_batch(
    request: BatchPredictionRequest,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    التنبؤ بأهلية الترقية لعدة موظفين - Predict promotion eligibility for multiple employees

    Args:
        request: طلب التنبؤ الجماعي - Batch prediction request
        lang: اللغة - Language

    Returns:
        نتائج التنبؤ - Prediction results
    """
    try:
        # تحميل النموذج - Load model
        try:
            model = load_model()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail=get_message("model_not_found", lang)
            )

        # تحضير البيانات - Prepare data
        employees_data = [emp.model_dump() for emp in request.employees]
        df = pd.DataFrame(employees_data)

        # التنبؤ - Make predictions
        preds = model.predict(df)
        probas = model.predict_proba(df)

        # إنشاء النتائج - Create results
        results = []
        for i, (emp, pred, proba) in enumerate(zip(request.employees, preds, probas)):
            confidence = max(proba)
            results.append({
                "employee_index": i,
                "prediction": get_message("promotion_eligible", lang) if pred == 1 else get_message("promotion_not_eligible", lang),
                "promotion_eligible": bool(pred),
                "probability": {
                    "no": round(proba[0], 4),
                    "yes": round(proba[1], 4)
                },
                "confidence": round(confidence, 4)
            })

        logger.info(f"تنبؤ جماعي لـ {len(request.employees)} موظف")

        return {
            "detail": get_message("prediction_success", lang),
            "total_employees": len(request.employees),
            "eligible_count": sum(preds),
            "not_eligible_count": len(preds) - sum(preds),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في التنبؤ الجماعي: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("prediction_error", lang, error=str(e))
        )


def _generate_recommendation(emp: Employee, pred: int, proba: list, lang: str) -> str:
    """
    إنشاء توصية بناءً على التنبؤ - Generate recommendation based on prediction

    Args:
        emp: بيانات الموظف - Employee data
        pred: التنبؤ - Prediction
        proba: الاحتماليات - Probabilities
        lang: اللغة - Language

    Returns:
        التوصية - Recommendation
    """
    if lang == "ar":
        if pred == 1:
            if proba[1] > 0.8:
                return "الموظف مؤهل بشكل كبير للترقية. يُنصح بالمضي قدماً في عملية الترقية."
            else:
                return "الموظف مؤهل للترقية، لكن يُنصح بمراجعة الأداء والمهارات قبل اتخاذ القرار النهائي."
        else:
            recommendations = []
            if emp.performance_score < 70:
                recommendations.append("تحسين الأداء الوظيفي")
            if emp.training_hours < 20:
                recommendations.append("زيادة ساعات التدريب")
            if emp.awards == 0:
                recommendations.append("السعي للحصول على جوائز وتقديرات")

            if recommendations:
                return f"الموظف غير مؤهل حالياً للترقية. يُنصح بـ: {', '.join(recommendations)}"
            else:
                return "الموظف غير مؤهل حالياً للترقية. يُنصح بمراجعة معايير الترقية."
    else:  # English
        if pred == 1:
            if proba[1] > 0.8:
                return "Employee is highly qualified for promotion. Recommend proceeding with promotion process."
            else:
                return "Employee is qualified for promotion, but recommend reviewing performance and skills before final decision."
        else:
            recommendations = []
            if emp.performance_score < 70:
                recommendations.append("improve job performance")
            if emp.training_hours < 20:
                recommendations.append("increase training hours")
            if emp.awards == 0:
                recommendations.append("pursue awards and recognition")

            if recommendations:
                return f"Employee is not currently qualified for promotion. Recommend: {', '.join(recommendations)}"
            else:
                return "Employee is not currently qualified for promotion. Recommend reviewing promotion criteria."
