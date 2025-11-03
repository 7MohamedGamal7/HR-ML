# تعليمات إعداد Cog - Cog Setup Instructions

<div dir="rtl">

## 📋 ملخص سريع

تم إنشاء تكامل كامل مع **Cog** لنظام الموارد البشرية الذكي. الآن يمكنك نشر نموذج التنبؤ بالترقيات كـ API مستقل باستخدام Cog.

---

## 📁 الملفات المنشأة

### 1. `cog.yaml`
ملف التكوين الرئيسي لـ Cog يحدد:
- إصدار Python (3.11)
- المكتبات المطلوبة
- أوامر البناء
- واجهة التنبؤ

### 2. `predict.py`
واجهة التنبؤ المتوافقة مع Cog تحتوي على:
- فئة `Predictor` مع دالة `setup()` لتحميل النموذج
- دالة `predict()` مع جميع المعاملات المطلوبة
- التحقق من صحة المدخلات
- دعم اللغتين العربية والإنجليزية
- توليد توصيات ذكية

### 3. `COG_GUIDE.md`
دليل شامل بالعربية يشرح:
- ما هو Cog وكيفية تثبيته
- خطوات بناء واختبار النموذج
- أمثلة الاستخدام
- النشر على Replicate وKubernetes
- استكشاف الأخطاء

### 4. `cog_helper.sh` (Linux/Mac)
سكريبت مساعد يوفر أوامر سهلة:
- `check` - فحص المتطلبات
- `build` - بناء صورة Cog
- `test` - اختبار التنبؤ
- `run` - تشغيل خادم HTTP
- `push` - النشر على Replicate

### 5. `cog_helper.bat` (Windows)
نفس السكريبت المساعد لنظام Windows

### 6. `test_cog.py`
سكريبت اختبار شامل يتحقق من:
- إعداد النموذج
- التنبؤ بالعربية والإنجليزية
- التحقق من صحة المدخلات
- التنبؤات الجماعية

---

## 🚀 خطوات الاستخدام (أنت الآن في حاوية Docker)

### الخطوة 1: التأكد من وجود النموذج المدرب

قبل استخدام Cog، يجب أن يكون لديك نموذج مدرب في `models/promotion_model.joblib`.

**إذا لم يكن لديك نموذج مدرب:**

```bash
# الخيار 1: استخدام FastAPI (في نافذة طرفية أخرى خارج الحاوية)
cd /f/hana_AI/workspace/hr-model
python run.py

# ثم في متصفح أو باستخدام curl:
# 1. رفع البيانات
curl -X POST "http://localhost:8000/upload/dataset" -F "file=@sample_data.csv"

# 2. تدريب النموذج
curl -X POST "http://localhost:8000/train/" -H "Content-Type: application/json" -d '{"model_type": "random_forest", "use_cross_validation": true}'
```

**أو الخيار 2: استخدام Python مباشرة:**

```bash
# في مجلد المشروع (خارج حاوية Cog)
cd /f/hana_AI/workspace/hr-model

python -c "
import pandas as pd
from app.model_utils import build_and_train, save_model
from app.data_utils import clean_df

# تحميل البيانات
df = pd.read_csv('sample_data.csv')
df = clean_df(df)

# فصل الميزات والهدف
X = df.drop('promotion_eligible', axis=1)
y = df['promotion_eligible']

# تدريب النموذج
print('Training model...')
model = build_and_train(X, y, model_type='random_forest')

# حفظ النموذج
print('Saving model...')
save_model(model)
print('Model saved successfully!')
"
```

### الخطوة 2: نسخ الملفات إلى الحاوية (إذا لزم الأمر)

إذا كنت داخل حاوية `cog-env` وتحتاج إلى نسخ الملفات:

```bash
# من خارج الحاوية (في نافذة طرفية جديدة)
docker cp /f/hana_AI/workspace/hr-model/. cog-env:/workspace/

# أو إذا كان لديك volume mount:
# تأكد من أن مجلد المشروع متصل بالحاوية
```

### الخطوة 3: بناء صورة Cog

```bash
# داخل حاوية cog-env أو على نظامك المحلي
cd /workspace  # أو المسار إلى مجلد المشروع

# بناء الصورة
cog build -t hr-ml-model

# هذا سيستغرق بضع دقائق في المرة الأولى
```

### الخطوة 4: اختبار التنبؤ

```bash
# اختبار بسيط
cog predict \
  -i experience=5.0 \
  -i education_level=7 \
  -i performance_score=85.0 \
  -i training_hours=40.0 \
  -i awards=2 \
  -i avg_work_hours=8.5 \
  -i department="it" \
  -i gender="male" \
  -i language="ar"
```

**النتيجة المتوقعة:**
```json
{
  "التنبؤ": "مؤهل للترقية",
  "احتمالية_الترقية": 85.5,
  "احتمالية_عدم_الترقية": 14.5,
  "مستوى_الثقة": "high",
  "التوصيات": [
    "✅ الموظف مؤهل للترقية بناءً على الأداء الحالي"
  ],
  "بيانات_الموظف": {...},
  "الطابع_الزمني": "2024-01-01T12:00:00"
}
```

### الخطوة 5: تشغيل خادم HTTP

```bash
# تشغيل الخادم على المنفذ 5000
cog run -p 5000

# الآن يمكنك الوصول إلى:
# - API: http://localhost:5000
# - الوثائق: http://localhost:5000/docs
# - OpenAPI: http://localhost:5000/openapi.json
```

### الخطوة 6: اختبار API

في نافذة طرفية جديدة:

```bash
# اختبار عبر curl
curl -X POST http://localhost:5000/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "experience": 10.0,
      "education_level": 9,
      "performance_score": 95.0,
      "training_hours": 80.0,
      "awards": 5,
      "avg_work_hours": 9.5,
      "department": "it",
      "gender": "male",
      "language": "ar"
    }
  }'
```

---

## 🧪 اختبار التكامل

قبل استخدام Cog، يمكنك اختبار واجهة التنبؤ:

```bash
# تشغيل سكريبت الاختبار
python test_cog.py

# سيقوم بتشغيل 6 اختبارات:
# 1. Setup - تحميل النموذج
# 2. Arabic Prediction - تنبؤ بالعربية
# 3. English Prediction - تنبؤ بالإنجليزية
# 4. Invalid Department - التحقق من القسم
# 5. Invalid Gender - التحقق من الجنس
# 6. Batch Predictions - تنبؤات متعددة
```

---

## 🔧 استخدام السكريبت المساعد

### Linux/Mac

```bash
# إعطاء صلاحيات التنفيذ
chmod +x cog_helper.sh

# فحص المتطلبات
./cog_helper.sh check

# بناء الصورة
./cog_helper.sh build

# اختبار التنبؤ
./cog_helper.sh test

# تشغيل الخادم
./cog_helper.sh run 5000

# النشر على Replicate
./cog_helper.sh push your-username
```

### Windows

```cmd
REM فحص المتطلبات
cog_helper.bat check

REM بناء الصورة
cog_helper.bat build

REM اختبار التنبؤ
cog_helper.bat test

REM تشغيل الخادم
cog_helper.bat run 5000

REM النشر على Replicate
cog_helper.bat push your-username
```

---

## 📦 النشر

### 1. النشر على Replicate

```bash
# تسجيل الدخول
cog login

# دفع النموذج
cog push r8.im/your-username/hr-ml-model

# الآن يمكن استخدام النموذج عبر:
# https://replicate.com/your-username/hr-ml-model
```

### 2. النشر على Docker Hub

```bash
# وسم الصورة
docker tag hr-ml-model your-username/hr-ml-model:latest

# دفع الصورة
docker push your-username/hr-ml-model:latest

# تشغيل من Docker Hub
docker run -p 5000:5000 your-username/hr-ml-model:latest
```

### 3. النشر على خادم

```bash
# نسخ الصورة إلى الخادم
docker save hr-ml-model | gzip > hr-ml-model.tar.gz
scp hr-ml-model.tar.gz user@server:/path/

# على الخادم
docker load < hr-ml-model.tar.gz
docker run -d -p 5000:5000 --name hr-ml hr-ml-model
```

---

## 🆚 Cog vs FastAPI

| الميزة | Cog | FastAPI (الحالي) |
|--------|-----|------------------|
| **سهولة النشر** | ⭐⭐⭐⭐⭐ سهل جداً | ⭐⭐⭐ متوسط |
| **نقاط نهاية متعددة** | ⭐⭐ محدود | ⭐⭐⭐⭐⭐ غير محدود |
| **إدارة السياسات** | ❌ غير مدعوم | ✅ مدعوم كاملاً |
| **تحليل الأداء** | ❌ غير مدعوم | ✅ مدعوم كاملاً |
| **التنبؤ بالترقيات** | ✅ مدعوم | ✅ مدعوم |
| **التكامل مع Replicate** | ✅ مدمج | ❌ غير مدعوم |
| **المرونة** | ⭐⭐⭐ محدود | ⭐⭐⭐⭐⭐ عالي |

**التوصية:**
- استخدم **Cog** إذا كنت تريد نشر نموذج التنبؤ فقط بسرعة
- استخدم **FastAPI** إذا كنت تريد النظام الكامل مع جميع الميزات

---

## ❓ الأسئلة الشائعة

### س: هل يمكن استخدام Cog و FastAPI معاً؟

نعم! يمكنك:
- استخدام FastAPI للنظام الكامل (تدريب، سياسات، تحليل)
- استخدام Cog لنشر نموذج التنبؤ فقط على Replicate

### س: هل يدعم Cog جميع ميزات النظام؟

لا، Cog يدعم فقط التنبؤ بالترقيات. للميزات الأخرى (السياسات، تحليل الأداء، إلخ)، استخدم FastAPI.

### س: كيف أحدث النموذج في Cog؟

```bash
# 1. درب نموذج جديد
python run.py  # ثم استخدم /train endpoint

# 2. أعد بناء صورة Cog
cog build -t hr-ml-model

# 3. أعد النشر
cog push r8.im/your-username/hr-ml-model
```

---

## 📚 الموارد

- **COG_GUIDE.md**: دليل شامل بالعربية
- **README.md**: وثائق النظام الكامل
- **QUICKSTART.md**: دليل البدء السريع
- [Cog Documentation](https://github.com/replicate/cog)
- [Replicate Platform](https://replicate.com/)

---

</div>

## English Quick Reference

### Prerequisites
1. Train the model first (see Step 1 above)
2. Install Cog: https://github.com/replicate/cog

### Quick Start
```bash
# Build
cog build -t hr-ml-model

# Test
cog predict -i experience=5.0 -i education_level=7 -i performance_score=85.0 -i training_hours=40.0 -i awards=2 -i avg_work_hours=8.5 -i department="it" -i gender="male" -i language="en"

# Run server
cog run -p 5000

# Deploy
cog push r8.im/your-username/hr-ml-model
```

### Helper Scripts
```bash
# Linux/Mac
./cog_helper.sh check|build|test|run|push

# Windows
cog_helper.bat check|build|test|run|push
```

For full documentation, see COG_GUIDE.md (Arabic) or above.

