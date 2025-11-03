# دليل Cog للنظام - Cog Integration Guide

<div dir="rtl">

## نظرة عامة 📦

تم تكامل نظام الموارد البشرية الذكي مع **Cog** لتسهيل النشر والاستخدام. Cog هو أداة مفتوحة المصدر من Replicate لتغليف نماذج التعلم الآلي في حاويات Docker قياسية مع واجهة HTTP API.

### ما هو Cog؟

Cog يحول نماذج التعلم الآلي إلى حاويات Docker جاهزة للإنتاج مع:
- ✅ واجهة API تلقائية
- ✅ التحقق من صحة المدخلات
- ✅ وثائق OpenAPI
- ✅ نشر سهل على أي منصة

---

## المتطلبات الأساسية 🔧

### 1. تثبيت Cog

```bash
# Linux/Mac
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
sudo chmod +x /usr/local/bin/cog

# أو باستخدام Homebrew (Mac)
brew install cog

# التحقق من التثبيت
cog --version
```

### 2. تثبيت Docker

تأكد من تثبيت Docker على نظامك:
```bash
docker --version
```

---

## هيكل الملفات 📁

```
hr-model/
├── cog.yaml              # تكوين Cog
├── predict.py            # واجهة التنبؤ Cog
├── app/                  # وحدات التطبيق
│   ├── config.py
│   ├── model_utils.py
│   ├── data_utils.py
│   └── i18n.py
├── models/               # النماذج المدربة
│   └── promotion_model.joblib
├── requirements.txt      # التبعيات
└── COG_GUIDE.md         # هذا الملف
```

---

## الخطوة 1: تدريب النموذج 🎓

قبل استخدام Cog، يجب تدريب النموذج أولاً:

### الطريقة 1: باستخدام FastAPI

```bash
# تشغيل FastAPI
python run.py

# رفع البيانات
curl -X POST "http://localhost:8000/upload/dataset" \
  -F "file=@sample_data.csv"

# تدريب النموذج
curl -X POST "http://localhost:8000/train/" \
  -H "Content-Type: application/json" \
  -d '{"model_type": "random_forest", "use_cross_validation": true}'
```

### الطريقة 2: باستخدام Python مباشرة

```python
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
model = build_and_train(X, y, model_type="random_forest")

# حفظ النموذج
save_model(model)
```

تأكد من وجود الملف: `models/promotion_model.joblib`

---

## الخطوة 2: بناء صورة Cog 🏗️

```bash
# في مجلد المشروع
cd /path/to/hr-model

# بناء صورة Cog
cog build -t hr-ml-model

# هذا سيستغرق بضع دقائق في المرة الأولى
```

**ملاحظة**: تأكد من وجود ملف `promotion_model.joblib` في مجلد `models/` قبل البناء.

---

## الخطوة 3: اختبار النموذج محلياً 🧪

### اختبار سريع

```bash
cog predict -i experience=5.0 \
            -i education_level=7 \
            -i performance_score=85.0 \
            -i training_hours=40.0 \
            -i awards=2 \
            -i avg_work_hours=8.5 \
            -i department="it" \
            -i gender="male" \
            -i language="ar"
```

### اختبار مع ملف JSON

أنشئ ملف `test_input.json`:
```json
{
  "experience": 5.0,
  "education_level": 7,
  "performance_score": 85.0,
  "training_hours": 40.0,
  "awards": 2,
  "avg_work_hours": 8.5,
  "department": "it",
  "gender": "male",
  "language": "ar"
}
```

ثم:
```bash
cog predict < test_input.json
```

---

## الخطوة 4: تشغيل خادم HTTP 🌐

### تشغيل الخادم

```bash
cog run -p 5000
```

الآن يمكنك الوصول إلى:
- **API**: http://localhost:5000
- **الوثائق**: http://localhost:5000/docs
- **OpenAPI Schema**: http://localhost:5000/openapi.json

### اختبار API

```bash
# التنبؤ بالعربية
curl -X POST http://localhost:5000/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "experience": 5.0,
      "education_level": 7,
      "performance_score": 85.0,
      "training_hours": 40.0,
      "awards": 2,
      "avg_work_hours": 8.5,
      "department": "it",
      "gender": "male",
      "language": "ar"
    }
  }'

# التنبؤ بالإنجليزية
curl -X POST http://localhost:5000/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "experience": 3.0,
      "education_level": 6,
      "performance_score": 70.0,
      "training_hours": 25.0,
      "awards": 1,
      "avg_work_hours": 8.0,
      "department": "hr",
      "gender": "female",
      "language": "en"
    }
  }'
```

---

## الخطوة 5: النشر 🚀

### النشر على Replicate

```bash
# تسجيل الدخول
cog login

# دفع النموذج
cog push r8.im/your-username/hr-ml-model
```

### النشر على Docker Hub

```bash
# وسم الصورة
docker tag hr-ml-model your-dockerhub-username/hr-ml-model:latest

# دفع الصورة
docker push your-dockerhub-username/hr-ml-model:latest

# تشغيل من Docker Hub
docker run -p 5000:5000 your-dockerhub-username/hr-ml-model:latest
```

### النشر على Kubernetes

أنشئ ملف `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hr-ml-model
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hr-ml-model
  template:
    metadata:
      labels:
        app: hr-ml-model
    spec:
      containers:
      - name: hr-ml-model
        image: your-dockerhub-username/hr-ml-model:latest
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: hr-ml-service
spec:
  selector:
    app: hr-ml-model
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

نشر:
```bash
kubectl apply -f k8s-deployment.yaml
```

---

## أمثلة الاستخدام 💡

### مثال 1: موظف مؤهل للترقية

```bash
cog predict \
  -i experience=10.0 \
  -i education_level=9 \
  -i performance_score=95.0 \
  -i training_hours=80.0 \
  -i awards=5 \
  -i avg_work_hours=9.5 \
  -i department="it" \
  -i gender="male" \
  -i language="ar"
```

**النتيجة المتوقعة**:
```json
{
  "التنبؤ": "مؤهل للترقية",
  "احتمالية_الترقية": 95.5,
  "احتمالية_عدم_الترقية": 4.5,
  "مستوى_الثقة": "high",
  "التوصيات": [
    "✅ الموظف مؤهل للترقية بناءً على الأداء الحالي",
    "🌟 احتمالية عالية جداً للترقية - يُنصح بالمتابعة الفورية"
  ]
}
```

### مثال 2: موظف يحتاج تحسين

```bash
cog predict \
  -i experience=2.0 \
  -i education_level=5 \
  -i performance_score=65.0 \
  -i training_hours=15.0 \
  -i awards=0 \
  -i avg_work_hours=7.5 \
  -i department="finance" \
  -i gender="female" \
  -i language="ar"
```

**النتيجة المتوقعة**:
```json
{
  "التنبؤ": "غير مؤهل للترقية",
  "احتمالية_الترقية": 15.2,
  "احتمالية_عدم_الترقية": 84.8,
  "مستوى_الثقة": "high",
  "التوصيات": [
    "⚠️ الموظف غير مؤهل للترقية حالياً",
    "📈 تحسين درجة الأداء من خلال تحديد أهداف واضحة",
    "📚 زيادة ساعات التدريب والتطوير المهني",
    "🏆 السعي للحصول على جوائز وتقديرات",
    "⏳ اكتساب المزيد من الخبرة في المجال"
  ]
}
```

---

## استكشاف الأخطاء 🔍

### الخطأ: "Model not found"

**الحل**:
```bash
# تأكد من وجود النموذج
ls -la models/promotion_model.joblib

# إذا لم يكن موجوداً، درب النموذج أولاً
python run.py
# ثم استخدم /upload و /train endpoints
```

### الخطأ: "Invalid department"

**الحل**: استخدم أحد الأقسام الصالحة:
- `it`
- `hr`
- `sales`
- `finance`
- `marketing`
- `operations`

### الخطأ: "Cog build failed"

**الحل**:
```bash
# تنظيف الذاكرة المؤقتة
cog build --no-cache -t hr-ml-model

# أو استخدم Docker مباشرة
docker build -t hr-ml-model .
```

---

## المقارنة: Cog vs FastAPI 🔄

| الميزة | Cog | FastAPI |
|--------|-----|---------|
| سهولة النشر | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| المرونة | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| التوثيق التلقائي | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| التكامل مع Replicate | ⭐⭐⭐⭐⭐ | ❌ |
| نقاط نهاية متعددة | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| إدارة الحالة | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**التوصية**: 
- استخدم **Cog** للنشر السريع ونماذج التنبؤ البسيطة
- استخدم **FastAPI** للتطبيقات المعقدة مع نقاط نهاية متعددة

---

## الموارد الإضافية 📚

- [Cog Documentation](https://github.com/replicate/cog)
- [Replicate Platform](https://replicate.com/)
- [Docker Documentation](https://docs.docker.com/)
- [README.md](./README.md) - الوثائق الكاملة للمشروع

---

</div>

## English Quick Reference

### Build
```bash
cog build -t hr-ml-model
```

### Test
```bash
cog predict -i experience=5.0 -i education_level=7 -i performance_score=85.0 -i training_hours=40.0 -i awards=2 -i avg_work_hours=8.5 -i department="it" -i gender="male" -i language="en"
```

### Run Server
```bash
cog run -p 5000
```

### Deploy to Replicate
```bash
cog login
cog push r8.im/your-username/hr-ml-model
```

For full documentation, see above (Arabic) or README.md.

