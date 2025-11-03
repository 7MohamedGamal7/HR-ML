"""
Cog Prediction Interface for HR-ML System
واجهة التنبؤ Cog لنظام الموارد البشرية الذكي

This file provides the Cog-compatible prediction interface for the HR promotion prediction model.
"""

from cog import BasePredictor, Input, Path as CogPath
from typing import Dict, Any, List, Optional
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Import our existing utilities
from app.config import (
    PROMOTION_MODEL_PATH,
    MIN_EXPERIENCE, MAX_EXPERIENCE,
    MIN_EDUCATION, MAX_EDUCATION,
    MIN_PERFORMANCE, MAX_PERFORMANCE,
    MIN_TRAINING_HOURS, MAX_TRAINING_HOURS,
    MIN_AWARDS, MAX_AWARDS,
    MIN_WORK_HOURS, MAX_WORK_HOURS,
    VALID_DEPARTMENTS, VALID_GENDERS
)


class Predictor(BasePredictor):
    """
    HR Promotion Prediction Model
    نموذج التنبؤ بالترقيات
    
    This predictor loads the trained promotion model and provides
    predictions for employee promotion eligibility.
    """
    
    def setup(self):
        """
        Load the model into memory to make running multiple predictions efficient.
        تحميل النموذج إلى الذاكرة لجعل التنبؤات المتعددة فعالة.
        """
        print("🚀 Loading HR Promotion Model...")
        
        # Check if model exists
        if not PROMOTION_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {PROMOTION_MODEL_PATH}. "
                "Please train the model first using the FastAPI endpoint."
            )
        
        # Load the trained model
        self.model = joblib.load(PROMOTION_MODEL_PATH)
        print(f"✅ Model loaded successfully from {PROMOTION_MODEL_PATH}")
        
        # Store valid values for validation
        self.valid_departments = VALID_DEPARTMENTS
        self.valid_genders = VALID_GENDERS
        
        print("✅ Predictor setup complete!")
    
    def predict(
        self,
        experience: float = Input(
            description="Years of experience - سنوات الخبرة",
            ge=MIN_EXPERIENCE,
            le=MAX_EXPERIENCE,
            default=5.0
        ),
        education_level: int = Input(
            description="Education level (0-10) - المستوى التعليمي",
            ge=MIN_EDUCATION,
            le=MAX_EDUCATION,
            default=7
        ),
        performance_score: float = Input(
            description="Performance score (0-100) - درجة الأداء",
            ge=MIN_PERFORMANCE,
            le=MAX_PERFORMANCE,
            default=85.0
        ),
        training_hours: float = Input(
            description="Training hours - ساعات التدريب",
            ge=MIN_TRAINING_HOURS,
            le=MAX_TRAINING_HOURS,
            default=40.0
        ),
        awards: int = Input(
            description="Number of awards - عدد الجوائز",
            ge=MIN_AWARDS,
            le=MAX_AWARDS,
            default=2
        ),
        avg_work_hours: float = Input(
            description="Average daily work hours - متوسط ساعات العمل اليومية",
            ge=MIN_WORK_HOURS,
            le=MAX_WORK_HOURS,
            default=8.5
        ),
        department: str = Input(
            description=f"Department - القسم. Valid values: {', '.join(VALID_DEPARTMENTS)}",
            default="it"
        ),
        gender: str = Input(
            description=f"Gender - الجنس. Valid values: {', '.join(VALID_GENDERS)}",
            default="male"
        ),
        language: str = Input(
            description="Response language - لغة الاستجابة (ar/en)",
            default="ar",
            choices=["ar", "en"]
        )
    ) -> Dict[str, Any]:
        """
        Predict promotion eligibility for an employee.
        التنبؤ بأهلية الترقية للموظف.
        
        Args:
            experience: Years of experience
            education_level: Education level (0-10)
            performance_score: Performance score (0-100)
            training_hours: Training hours completed
            awards: Number of awards received
            avg_work_hours: Average daily work hours
            department: Employee department
            gender: Employee gender
            language: Response language (ar/en)
        
        Returns:
            Dictionary containing prediction results and recommendations
        """
        
        # Validate department and gender
        department = department.lower()
        gender = gender.lower()
        
        if department not in self.valid_departments:
            return {
                "error": f"Invalid department. Must be one of: {', '.join(self.valid_departments)}",
                "error_ar": f"قسم غير صالح. يجب أن يكون أحد: {', '.join(self.valid_departments)}"
            }
        
        if gender not in self.valid_genders:
            return {
                "error": f"Invalid gender. Must be one of: {', '.join(self.valid_genders)}",
                "error_ar": f"جنس غير صالح. يجب أن يكون أحد: {', '.join(self.valid_genders)}"
            }
        
        # Prepare input data
        input_data = pd.DataFrame([{
            'experience': experience,
            'education_level': education_level,
            'performance_score': performance_score,
            'training_hours': training_hours,
            'awards': awards,
            'avg_work_hours': avg_work_hours,
            'department': department,
            'gender': gender
        }])
        
        # Make prediction
        try:
            prediction = self.model.predict(input_data)[0]
            probabilities = self.model.predict_proba(input_data)[0]
            
            # Get probability for promotion
            promotion_probability = float(probabilities[1])
            no_promotion_probability = float(probabilities[0])
            
            # Determine confidence level
            confidence = "high" if max(probabilities) > 0.8 else "medium" if max(probabilities) > 0.6 else "low"
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                prediction, promotion_probability, input_data.iloc[0], language
            )
            
            # Prepare response based on language
            if language == "ar":
                result = {
                    "التنبؤ": "مؤهل للترقية" if prediction == 1 else "غير مؤهل للترقية",
                    "احتمالية_الترقية": round(promotion_probability * 100, 2),
                    "احتمالية_عدم_الترقية": round(no_promotion_probability * 100, 2),
                    "مستوى_الثقة": confidence,
                    "التوصيات": recommendations,
                    "بيانات_الموظف": {
                        "الخبرة": experience,
                        "المستوى_التعليمي": education_level,
                        "درجة_الأداء": performance_score,
                        "ساعات_التدريب": training_hours,
                        "الجوائز": awards,
                        "متوسط_ساعات_العمل": avg_work_hours,
                        "القسم": department,
                        "الجنس": gender
                    },
                    "الطابع_الزمني": datetime.now().isoformat()
                }
            else:
                result = {
                    "prediction": "Eligible for Promotion" if prediction == 1 else "Not Eligible for Promotion",
                    "promotion_probability": round(promotion_probability * 100, 2),
                    "no_promotion_probability": round(no_promotion_probability * 100, 2),
                    "confidence_level": confidence,
                    "recommendations": recommendations,
                    "employee_data": {
                        "experience": experience,
                        "education_level": education_level,
                        "performance_score": performance_score,
                        "training_hours": training_hours,
                        "awards": awards,
                        "avg_work_hours": avg_work_hours,
                        "department": department,
                        "gender": gender
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Prediction failed: {str(e)}",
                "error_ar": f"فشل التنبؤ: {str(e)}"
            }
    
    def _generate_recommendations(
        self,
        prediction: int,
        probability: float,
        employee_data: pd.Series,
        language: str
    ) -> List[str]:
        """
        Generate personalized recommendations based on prediction.
        إنشاء توصيات مخصصة بناءً على التنبؤ.
        """
        recommendations = []
        
        if language == "ar":
            if prediction == 1:
                recommendations.append("✅ الموظف مؤهل للترقية بناءً على الأداء الحالي")
                if probability > 0.9:
                    recommendations.append("🌟 احتمالية عالية جداً للترقية - يُنصح بالمتابعة الفورية")
            else:
                recommendations.append("⚠️ الموظف غير مؤهل للترقية حالياً")
                
                # Specific recommendations based on weak areas
                if employee_data['performance_score'] < 75:
                    recommendations.append("📈 تحسين درجة الأداء من خلال تحديد أهداف واضحة")
                
                if employee_data['training_hours'] < 30:
                    recommendations.append("📚 زيادة ساعات التدريب والتطوير المهني")
                
                if employee_data['awards'] < 2:
                    recommendations.append("🏆 السعي للحصول على جوائز وتقديرات")
                
                if employee_data['experience'] < 3:
                    recommendations.append("⏳ اكتساب المزيد من الخبرة في المجال")
        else:
            if prediction == 1:
                recommendations.append("✅ Employee is eligible for promotion based on current performance")
                if probability > 0.9:
                    recommendations.append("🌟 Very high promotion probability - immediate follow-up recommended")
            else:
                recommendations.append("⚠️ Employee is not currently eligible for promotion")
                
                if employee_data['performance_score'] < 75:
                    recommendations.append("📈 Improve performance score through clear goal setting")
                
                if employee_data['training_hours'] < 30:
                    recommendations.append("📚 Increase training hours and professional development")
                
                if employee_data['awards'] < 2:
                    recommendations.append("🏆 Strive for awards and recognition")
                
                if employee_data['experience'] < 3:
                    recommendations.append("⏳ Gain more experience in the field")
        
        return recommendations

