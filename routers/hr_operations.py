"""
موجه العمليات البشرية - HR Operations Router
يوفر نقاط نهاية لعمليات الموارد البشرية المتقدمة
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger
import pandas as pd
import numpy as np

from app.i18n import get_message
from app.config import PERFORMANCE_FEATURES

router = APIRouter(prefix="/hr", tags=["عمليات الموارد البشرية - HR Operations"])


class PerformanceAnalysisRequest(BaseModel):
    """طلب تحليل الأداء - Performance analysis request"""
    performance_score: float = Field(..., ge=0, le=100)
    training_hours: float = Field(..., ge=0)
    awards: int = Field(..., ge=0)
    avg_work_hours: float = Field(..., ge=0, le=24)
    experience: float = Field(..., ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "performance_score": 85.0,
                "training_hours": 40.0,
                "awards": 2,
                "avg_work_hours": 8.5,
                "experience": 5.0
            }
        }


class LeaveRecommendationRequest(BaseModel):
    """طلب توصية الإجازة - Leave recommendation request"""
    employee_experience: float = Field(..., ge=0, description="سنوات الخبرة")
    current_leave_balance: int = Field(..., ge=0, description="رصيد الإجازات الحالي")
    department: str = Field(..., description="القسم")
    performance_score: float = Field(..., ge=0, le=100, description="درجة الأداء")
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_experience": 5.0,
                "current_leave_balance": 15,
                "department": "it",
                "performance_score": 85.0
            }
        }


class ComplianceCheckRequest(BaseModel):
    """طلب فحص الامتثال - Compliance check request"""
    employee_data: Dict[str, Any] = Field(..., description="بيانات الموظف")
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_data": {
                    "experience": 5.0,
                    "education_level": 7,
                    "training_hours": 40.0,
                    "avg_work_hours": 8.5,
                    "department": "it"
                }
            }
        }


@router.post("/performance-analysis")
async def analyze_performance(
    request: PerformanceAnalysisRequest,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    تحليل أداء الموظف - Analyze employee performance
    
    Args:
        request: بيانات الأداء - Performance data
        lang: اللغة - Language
    
    Returns:
        تحليل الأداء - Performance analysis
    """
    try:
        # حساب النتيجة الإجمالية - Calculate overall score
        weights = {
            'performance_score': 0.4,
            'training_hours': 0.2,
            'awards': 0.2,
            'avg_work_hours': 0.1,
            'experience': 0.1
        }
        
        # تطبيع القيم - Normalize values
        normalized_training = min(request.training_hours / 100, 1.0)
        normalized_awards = min(request.awards / 10, 1.0)
        normalized_work_hours = request.avg_work_hours / 24
        normalized_experience = min(request.experience / 20, 1.0)
        
        overall_score = (
            weights['performance_score'] * (request.performance_score / 100) +
            weights['training_hours'] * normalized_training +
            weights['awards'] * normalized_awards +
            weights['avg_work_hours'] * normalized_work_hours +
            weights['experience'] * normalized_experience
        ) * 100
        
        # تحديد مستوى الأداء - Determine performance level
        if overall_score >= 85:
            level = get_message("performance_excellent", lang)
            level_en = "excellent"
        elif overall_score >= 70:
            level = get_message("performance_good", lang)
            level_en = "good"
        elif overall_score >= 55:
            level = get_message("performance_average", lang)
            level_en = "average"
        elif overall_score >= 40:
            level = get_message("performance_below_average", lang)
            level_en = "below_average"
        else:
            level = get_message("performance_poor", lang)
            level_en = "poor"
        
        # إنشاء التوصيات - Generate recommendations
        recommendations = []
        if request.performance_score < 70:
            recommendations.append({
                "area": "الأداء الوظيفي" if lang == "ar" else "Job Performance",
                "suggestion": "تحسين الأداء من خلال التدريب والتطوير" if lang == "ar" else "Improve performance through training and development"
            })
        
        if request.training_hours < 30:
            recommendations.append({
                "area": "التدريب" if lang == "ar" else "Training",
                "suggestion": "زيادة ساعات التدريب السنوية" if lang == "ar" else "Increase annual training hours"
            })
        
        if request.awards == 0:
            recommendations.append({
                "area": "الإنجازات" if lang == "ar" else "Achievements",
                "suggestion": "السعي للحصول على جوائز وتقديرات" if lang == "ar" else "Pursue awards and recognition"
            })
        
        # نقاط القوة - Strengths
        strengths = []
        if request.performance_score >= 80:
            strengths.append("أداء وظيفي ممتاز" if lang == "ar" else "Excellent job performance")
        if request.training_hours >= 40:
            strengths.append("التزام قوي بالتدريب" if lang == "ar" else "Strong commitment to training")
        if request.awards >= 2:
            strengths.append("إنجازات متميزة" if lang == "ar" else "Outstanding achievements")
        
        return {
            "detail": get_message("performance_analyzed", lang),
            "overall_score": round(overall_score, 2),
            "performance_level": level,
            "performance_level_code": level_en,
            "strengths": strengths,
            "recommendations": recommendations,
            "metrics": {
                "performance_score": request.performance_score,
                "training_hours": request.training_hours,
                "awards": request.awards,
                "avg_work_hours": request.avg_work_hours,
                "experience": request.experience
            }
        }
    
    except Exception as e:
        logger.error(f"خطأ في تحليل الأداء: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.post("/leave-recommendation")
async def recommend_leave(
    request: LeaveRecommendationRequest,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    توصية بالإجازات - Leave recommendation
    
    Args:
        request: بيانات الإجازة - Leave data
        lang: اللغة - Language
    
    Returns:
        توصيات الإجازة - Leave recommendations
    """
    try:
        # حساب الإجازة السنوية المستحقة - Calculate annual leave entitlement
        base_leave = 21  # أيام أساسية - Base days
        
        # إضافة أيام بناءً على الخبرة - Add days based on experience
        if request.employee_experience >= 10:
            base_leave += 7
        elif request.employee_experience >= 5:
            base_leave += 3
        
        # إضافة أيام بناءً على الأداء - Add days based on performance
        if request.performance_score >= 90:
            base_leave += 2
        elif request.performance_score >= 80:
            base_leave += 1
        
        # حساب الأيام المتبقية - Calculate remaining days
        remaining_days = base_leave - request.current_leave_balance
        
        # التوصيات - Recommendations
        recommendations = []
        
        if remaining_days > 15:
            recommendations.append({
                "type": "تحذير" if lang == "ar" else "Warning",
                "message": f"لديك {remaining_days} يوم إجازة متبقي. يُنصح باستخدام بعض الإجازات قريباً." if lang == "ar" 
                          else f"You have {remaining_days} leave days remaining. Recommend using some leave soon."
            })
        elif remaining_days < 5:
            recommendations.append({
                "type": "تنبيه" if lang == "ar" else "Alert",
                "message": f"لديك {remaining_days} يوم إجازة فقط. تأكد من التخطيط بعناية." if lang == "ar"
                          else f"You only have {remaining_days} leave days. Ensure careful planning."
            })
        
        # أفضل وقت للإجازة - Best time for leave
        best_time = "الربع الثاني أو الثالث من السنة" if lang == "ar" else "Second or third quarter of the year"
        
        return {
            "detail": get_message("recommendations_generated", lang),
            "annual_entitlement": base_leave,
            "current_balance": request.current_leave_balance,
            "remaining_days": remaining_days,
            "recommendations": recommendations,
            "best_time_for_leave": best_time,
            "leave_policy_link": "/policies/search/query?category=leave"
        }
    
    except Exception as e:
        logger.error(f"خطأ في توصية الإجازة: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.post("/compliance-check")
async def check_compliance(
    request: ComplianceCheckRequest,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    فحص الامتثال للوائح - Compliance check
    
    Args:
        request: بيانات الموظف - Employee data
        lang: اللغة - Language
    
    Returns:
        نتائج فحص الامتثال - Compliance check results
    """
    try:
        issues = []
        warnings = []
        
        emp_data = request.employee_data
        
        # فحص ساعات العمل - Check work hours
        if emp_data.get('avg_work_hours', 0) > 10:
            issues.append({
                "severity": "عالية" if lang == "ar" else "High",
                "issue": "ساعات العمل تتجاوز الحد المسموح" if lang == "ar" else "Work hours exceed allowed limit",
                "regulation": "قانون العمل - المادة 98" if lang == "ar" else "Labor Law - Article 98"
            })
        elif emp_data.get('avg_work_hours', 0) > 9:
            warnings.append({
                "severity": "متوسطة" if lang == "ar" else "Medium",
                "issue": "ساعات العمل قريبة من الحد الأقصى" if lang == "ar" else "Work hours close to maximum limit"
            })
        
        # فحص التدريب - Check training
        if emp_data.get('training_hours', 0) < 20:
            warnings.append({
                "severity": "منخفضة" if lang == "ar" else "Low",
                "issue": "ساعات التدريب أقل من الموصى به" if lang == "ar" else "Training hours below recommended"
            })
        
        # فحص المستوى التعليمي - Check education level
        if emp_data.get('education_level', 0) < 5:
            warnings.append({
                "severity": "منخفضة" if lang == "ar" else "Low",
                "issue": "المستوى التعليمي أقل من المتوسط" if lang == "ar" else "Education level below average"
            })
        
        # النتيجة - Result
        is_compliant = len(issues) == 0
        
        return {
            "detail": get_message("compliance_check_passed", lang) if is_compliant else get_message("compliance_check_failed", lang),
            "is_compliant": is_compliant,
            "total_issues": len(issues),
            "total_warnings": len(warnings),
            "issues": issues,
            "warnings": warnings,
            "checked_at": pd.Timestamp.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"خطأ في فحص الامتثال: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.get("/dashboard/summary")
async def get_hr_dashboard(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    لوحة معلومات الموارد البشرية - HR Dashboard
    
    Args:
        lang: اللغة - Language
    
    Returns:
        ملخص لوحة المعلومات - Dashboard summary
    """
    try:
        # هذا مثال توضيحي - في التطبيق الحقيقي، ستأتي البيانات من قاعدة البيانات
        # This is a demo - in real app, data would come from database
        
        dashboard_data = {
            "total_employees": 0,
            "departments": [],
            "average_performance": 0,
            "promotion_eligible_count": 0,
            "compliance_status": {
                "compliant": 0,
                "non_compliant": 0
            },
            "recent_activities": []
        }
        
        return {
            "detail": get_message("success", lang),
            "dashboard": dashboard_data,
            "message": "لوحة المعلومات - يتطلب بيانات موظفين" if lang == "ar" else "Dashboard - Requires employee data"
        }
    
    except Exception as e:
        logger.error(f"خطأ في لوحة المعلومات: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )

