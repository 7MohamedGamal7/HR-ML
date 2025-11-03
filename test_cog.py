"""
Test script for Cog integration
سكريبت اختبار تكامل Cog

This script tests the Cog prediction interface without requiring Cog to be installed.
It simulates the Cog environment and validates the prediction logic.
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_predictor_setup():
    """Test if the predictor can be set up correctly"""
    print("🧪 Testing Predictor Setup...")
    
    try:
        from predict import Predictor
        
        predictor = Predictor()
        predictor.setup()
        
        print("✅ Predictor setup successful!")
        print(f"   Model loaded from: {predictor.model}")
        print(f"   Valid departments: {predictor.valid_departments}")
        print(f"   Valid genders: {predictor.valid_genders}")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Model not found: {e}")
        print("   Please train the model first using FastAPI or run:")
        print("   python -c \"from app.model_utils import build_and_train, save_model; import pandas as pd; df = pd.read_csv('sample_data.csv'); X = df.drop('promotion_eligible', axis=1); y = df['promotion_eligible']; model = build_and_train(X, y); save_model(model)\"")
        return False
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction_arabic():
    """Test prediction with Arabic language"""
    print("\n🧪 Testing Prediction (Arabic)...")
    
    try:
        from predict import Predictor
        
        predictor = Predictor()
        predictor.setup()
        
        # Test case: High-performing employee
        result = predictor.predict(
            experience=10.0,
            education_level=9,
            performance_score=95.0,
            training_hours=80.0,
            awards=5,
            avg_work_hours=9.5,
            department="it",
            gender="male",
            language="ar"
        )
        
        print("✅ Arabic prediction successful!")
        print(f"   Result: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # Validate response structure
        assert "التنبؤ" in result, "Missing prediction in Arabic response"
        assert "احتمالية_الترقية" in result, "Missing promotion probability"
        assert "التوصيات" in result, "Missing recommendations"
        
        print("✅ Response structure validated!")
        return True
        
    except Exception as e:
        print(f"❌ Arabic prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction_english():
    """Test prediction with English language"""
    print("\n🧪 Testing Prediction (English)...")
    
    try:
        from predict import Predictor
        
        predictor = Predictor()
        predictor.setup()
        
        # Test case: Low-performing employee
        result = predictor.predict(
            experience=2.0,
            education_level=5,
            performance_score=65.0,
            training_hours=15.0,
            awards=0,
            avg_work_hours=7.5,
            department="finance",
            gender="female",
            language="en"
        )
        
        print("✅ English prediction successful!")
        print(f"   Result: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # Validate response structure
        assert "prediction" in result, "Missing prediction in English response"
        assert "promotion_probability" in result, "Missing promotion probability"
        assert "recommendations" in result, "Missing recommendations"
        
        print("✅ Response structure validated!")
        return True
        
    except Exception as e:
        print(f"❌ English prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_department():
    """Test validation for invalid department"""
    print("\n🧪 Testing Invalid Department Validation...")
    
    try:
        from predict import Predictor
        
        predictor = Predictor()
        predictor.setup()
        
        result = predictor.predict(
            experience=5.0,
            education_level=7,
            performance_score=85.0,
            training_hours=40.0,
            awards=2,
            avg_work_hours=8.5,
            department="invalid_dept",
            gender="male",
            language="ar"
        )
        
        # Should return error
        assert "error" in result or "error_ar" in result, "Expected error for invalid department"
        
        print("✅ Invalid department validation successful!")
        print(f"   Error message: {result.get('error_ar', result.get('error'))}")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_gender():
    """Test validation for invalid gender"""
    print("\n🧪 Testing Invalid Gender Validation...")
    
    try:
        from predict import Predictor
        
        predictor = Predictor()
        predictor.setup()
        
        result = predictor.predict(
            experience=5.0,
            education_level=7,
            performance_score=85.0,
            training_hours=40.0,
            awards=2,
            avg_work_hours=8.5,
            department="it",
            gender="invalid_gender",
            language="ar"
        )
        
        # Should return error
        assert "error" in result or "error_ar" in result, "Expected error for invalid gender"
        
        print("✅ Invalid gender validation successful!")
        print(f"   Error message: {result.get('error_ar', result.get('error'))}")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_predictions():
    """Test multiple predictions"""
    print("\n🧪 Testing Batch Predictions...")
    
    try:
        from predict import Predictor
        
        predictor = Predictor()
        predictor.setup()
        
        test_cases = [
            {
                "name": "High Performer",
                "params": {
                    "experience": 10.0,
                    "education_level": 9,
                    "performance_score": 95.0,
                    "training_hours": 80.0,
                    "awards": 5,
                    "avg_work_hours": 9.5,
                    "department": "it",
                    "gender": "male",
                    "language": "en"
                }
            },
            {
                "name": "Average Performer",
                "params": {
                    "experience": 5.0,
                    "education_level": 7,
                    "performance_score": 75.0,
                    "training_hours": 35.0,
                    "awards": 2,
                    "avg_work_hours": 8.0,
                    "department": "hr",
                    "gender": "female",
                    "language": "en"
                }
            },
            {
                "name": "Low Performer",
                "params": {
                    "experience": 1.0,
                    "education_level": 4,
                    "performance_score": 60.0,
                    "training_hours": 10.0,
                    "awards": 0,
                    "avg_work_hours": 7.0,
                    "department": "operations",
                    "gender": "male",
                    "language": "en"
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            result = predictor.predict(**test_case["params"])
            results.append({
                "name": test_case["name"],
                "prediction": result.get("prediction", "N/A"),
                "probability": result.get("promotion_probability", 0)
            })
            print(f"   {test_case['name']}: {result.get('prediction', 'N/A')} ({result.get('promotion_probability', 0)}%)")
        
        print("✅ Batch predictions successful!")
        return True
        
    except Exception as e:
        print(f"❌ Batch predictions failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 HR-ML Cog Integration Test Suite")
    print("   نظام الموارد البشرية الذكي - اختبار تكامل Cog")
    print("=" * 60)
    
    tests = [
        ("Setup", test_predictor_setup),
        ("Arabic Prediction", test_prediction_arabic),
        ("English Prediction", test_prediction_english),
        ("Invalid Department", test_invalid_department),
        ("Invalid Gender", test_invalid_gender),
        ("Batch Predictions", test_batch_predictions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Cog integration is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

