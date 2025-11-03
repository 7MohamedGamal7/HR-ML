# دليل البدء السريع - Quick Start Guide

<div dir="rtl">

## البدء في 5 دقائق ⚡

### الخطوة 1: التثبيت

```bash
# استنساخ المشروع
git clone <repository-url>
cd hr-model

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

### الخطوة 2: تشغيل النظام

```bash
python run.py
```

سيعمل النظام على: http://localhost:8000

### الخطوة 3: استكشاف الواجهة

افتح المتصفح وانتقل إلى:
- **الوثائق التفاعلية**: http://localhost:8000/docs
- **الصفحة الرئيسية**: http://localhost:8000

### الخطوة 4: رفع البيانات

استخدم ملف البيانات النموذجي المرفق:

```bash
curl -X POST "http://localhost:8000/upload/dataset?lang=ar" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data.csv"
```

أو استخدم واجهة Swagger:
1. اذهب إلى http://localhost:8000/docs
2. ابحث عن `/upload/dataset`
3. اضغط "Try it out"
4. اختر ملف `sample_data.csv`
5. اضغط "Execute"

### الخطوة 5: تدريب النموذج

```bash
curl -X POST "http://localhost:8000/train/?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "random_forest",
    "use_cross_validation": true,
    "test_size": 0.2
  }'
```

أو عبر Swagger:
1. ابحث عن `/train/`
2. اضغط "Try it out"
3. اضغط "Execute"

### الخطوة 6: التنبؤ

```bash
curl -X POST "http://localhost:8000/predict/?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "experience": 5.0,
    "education_level": 7,
    "performance_score": 85.0,
    "training_hours": 40.0,
    "awards": 2,
    "avg_work_hours": 8.5,
    "department": "it",
    "gender": "male"
  }'
```

---

## البدء باستخدام Docker 🐳

### الطريقة الأسرع

```bash
# بناء وتشغيل
docker-compose up -d

# عرض السجلات
docker-compose logs -f

# الوصول للنظام
# افتح http://localhost:8000/docs
```

### إيقاف النظام

```bash
docker-compose down
```

---

## أمثلة سريعة 📝

### 1. فحص صحة النظام

```bash
curl "http://localhost:8000/health/?lang=ar"
```

### 2. إضافة سياسة

```bash
curl -X POST "http://localhost:8000/policies/?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "سياسة الإجازات",
    "content": "يحق لكل موظف 21 يوم إجازة سنوية",
    "category": "leave",
    "tags": ["إجازات"]
  }'
```

### 3. تحليل الأداء

```bash
curl -X POST "http://localhost:8000/hr/performance-analysis?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "performance_score": 85.0,
    "training_hours": 40.0,
    "awards": 2,
    "avg_work_hours": 8.5,
    "experience": 5.0
  }'
```

### 4. البحث في السياسات

```bash
curl "http://localhost:8000/policies/search/query?query=إجازة&lang=ar"
```

---

## الخطوات التالية 🚀

1. **اقرأ الوثائق الكاملة**: راجع `README.md` للحصول على معلومات مفصلة
2. **استكشف الواجهة**: جرب جميع نقاط النهاية في http://localhost:8000/docs
3. **أضف بياناتك**: استبدل `sample_data.csv` ببيانات شركتك
4. **خصص النظام**: عدّل الإعدادات في `app/config.py`
5. **انشر النظام**: استخدم Docker للنشر في الإنتاج

---

## المساعدة والدعم 💬

- **الوثائق الكاملة**: راجع `README.md`
- **استكشاف الأخطاء**: راجع قسم "دليل استكشاف الأخطاء" في README
- **الأسئلة**: افتح Issue على GitHub

---

</div>

## English Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run
```bash
python run.py
```

### 3. Access
- Docs: http://localhost:8000/docs
- API: http://localhost:8000

### 4. Upload Data
```bash
curl -X POST "http://localhost:8000/upload/dataset" \
  -F "file=@sample_data.csv"
```

### 5. Train Model
```bash
curl -X POST "http://localhost:8000/train/"
```

### 6. Predict
```bash
curl -X POST "http://localhost:8000/predict/" \
  -H "Content-Type: application/json" \
  -d '{"experience": 5.0, "education_level": 7, ...}'
```

For full documentation, see `README.md`.

