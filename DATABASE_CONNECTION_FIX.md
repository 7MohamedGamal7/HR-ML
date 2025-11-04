# 🔧 إصلاح مشكلة الاتصال بقاعدة البيانات - Database Connection Fix

## ✅ تم إصلاح المشكلة بنجاح!

تم إصلاح مشكلة عدم العثور على ODBC Driver 17 for SQL Server في Docker container.

**✅ تم التحقق من التثبيت:**
- ODBC Driver 17 for SQL Server مثبت ويعمل بنجاح
- النظام يعمل على المنفذ 1234
- جميع الوظائف جاهزة للاستخدام

---

## 🐛 المشكلة الأصلية

**رسالة الخطأ:**
```
فشل الاتصال بقاعدة البيانات - Connection failed: 
('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server' : file not found (0) (SQLDriverConnect)")
```

**السبب:**
- Docker container لم يكن يحتوي على Microsoft ODBC Driver 17 for SQL Server
- فقط unixODBC كان مثبتاً بدون drivers

---

## 🔧 الإصلاحات المنفذة

### 1. تحديث Dockerfile ✅

تم إضافة تثبيت Microsoft ODBC Driver 17 for SQL Server:

```dockerfile
# تثبيت Microsoft ODBC Driver 17 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

**ما تم تثبيته:**
- ✅ `msodbcsql17` - Microsoft ODBC Driver 17 for SQL Server
- ✅ `mssql-tools` - أدوات SQL Server (sqlcmd, bcp)
- ✅ `unixODBC` - مدير ODBC
- ✅ `unixodbc-dev` - ملفات التطوير

### 2. تحسين آلية Fallback في `app/database.py` ✅

تم إضافة وظائف جديدة:

#### **أ. `get_available_drivers()`**
- تحصل على قائمة جميع ODBC drivers المتاحة في النظام
- تساعد في تشخيص المشاكل

#### **ب. `get_best_driver()`**
- تختار أفضل driver متاح تلقائياً
- الترتيب من الأفضل إلى الأقل:
  1. ODBC Driver 18 for SQL Server
  2. ODBC Driver 17 for SQL Server ✅ (المثبت الآن)
  3. ODBC Driver 13 for SQL Server
  4. ODBC Driver 11 for SQL Server
  5. FreeTDS
  6. SQL Server

#### **ج. تحسين `get_pyodbc_connection()`**
- محاولة الاتصال بـ driver محدد أولاً
- إذا فشل، تجربة أفضل driver متاح تلقائياً
- رسائل خطأ أوضح للتشخيص

### 3. آلية Triple-Fallback المحسنة ✅

النظام الآن يحاول الاتصال بالترتيب التالي:

1. **pyodbc مع driver محدد** (ODBC Driver 17)
2. **pyodbc مع أفضل driver متاح** (تلقائي)
3. **pymssql** (Pure Python driver)
4. **SQLAlchemy مع pymssql** (آخر محاولة)

---

## 🚀 خطوات إعادة البناء والاختبار

### الخطوة 1: إعادة بناء Docker Container

```bash
# إيقاف Container الحالي
docker-compose down

# إعادة البناء بدون cache (مهم جداً!)
docker-compose build --no-cache

# تشغيل Container الجديد
docker-compose up -d
```

**ملاحظة مهمة:** يجب استخدام `--no-cache` لضمان تثبيت ODBC Driver الجديد.

### الخطوة 2: التحقق من التثبيت

```bash
# الدخول إلى Container
docker exec -it hr-ml-system bash

# التحقق من ODBC drivers المثبتة
odbcinst -q -d

# يجب أن ترى:
# [ODBC Driver 17 for SQL Server]
```

### الخطوة 3: اختبار الاتصال

#### **أ. من خلال API:**

```bash
# اختبار الاتصال (عربي)
curl -X GET "http://localhost:1234/train/database/test-connection?lang=ar"

# اختبار الاتصال (إنجليزي)
curl -X GET "http://localhost:1234/train/database/test-connection?lang=en"
```

#### **ب. من خلال واجهة الويب:**

1. افتح: `http://localhost:1234/static/database_connection.html`
2. أدخل معلومات الاتصال:
   - **Host:** عنوان SQL Server (مثل: `192.168.1.100` أو `sqlserver.example.com`)
   - **Port:** `1433` (الافتراضي)
   - **Database:** اسم قاعدة البيانات
   - **Username:** اسم المستخدم
   - **Password:** كلمة المرور
3. اضغط "اختبار الاتصال"

#### **ج. من خلال لوحة التحكم:**

1. افتح: `http://localhost:1234/static/dashboard/index.html`
2. انتقل إلى صفحة "قاعدة البيانات"
3. أدخل معلومات الاتصال
4. اضغط "اختبار الاتصال"

---

## ⚙️ إعداد قاعدة البيانات

### 1. تحديث ملف `.env`

قم بتحديث ملف `.env` بمعلومات قاعدة البيانات الخاصة بك:

```env
# إعدادات قاعدة البيانات - Database Settings
SQL_SERVER_HOST=your_server_address
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=your_database_name
SQL_SERVER_USERNAME=your_username
SQL_SERVER_PASSWORD=your_password
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_TIMEOUT=30
DEFAULT_EMPLOYEE_TABLE=Employees
```

**مثال:**
```env
SQL_SERVER_HOST=192.168.1.100
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourStrongPassword123!
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_TIMEOUT=30
DEFAULT_EMPLOYEE_TABLE=Employees
```

### 2. إنشاء جدول Employees في SQL Server

قم بتشغيل هذا الاستعلام في SQL Server:

```sql
CREATE TABLE Employees (
    -- معلومات أساسية - Basic Information
    Emp_ID INT PRIMARY KEY,
    Emp_Full_Name NVARCHAR(200),
    Emp_Phone1 NVARCHAR(20),
    Emp_Address NVARCHAR(500),
    Emp_Marital_Status NVARCHAR(50),
    Emp_Nationality NVARCHAR(100),
    People_With_Special_Needs NVARCHAR(10),
    National_ID NVARCHAR(50),
    Date_Birth DATE,
    Place_Birth NVARCHAR(200),
    
    -- معلومات العمل - Work Information
    Emp_Type NVARCHAR(100),
    Working_Condition NVARCHAR(100),
    Dept_Name NVARCHAR(200),
    Jop_Name NVARCHAR(200),
    Emp_Date_Hiring DATE,
    
    -- معلومات السيارة - Car Information
    Emp_Car NVARCHAR(10),
    Car_Ride_Time INT,
    Car_Pick_Up_Point NVARCHAR(200),
    
    -- معلومات التأمين - Insurance Information
    Insurance_Status NVARCHAR(100),
    Jop_Code_insurance NVARCHAR(50),
    Jop_Name_insurance NVARCHAR(200),
    Health_Card NVARCHAR(50),
    Health_Card_Expiration_Date DATE,
    Number_Insurance NVARCHAR(50),
    Date_Insurance_Start DATE,
    Insurance_Salary DECIMAL(18, 2),
    Percentage_Insurance_Payable DECIMAL(5, 2),
    Due_Insurance_Amount DECIMAL(18, 2),
    
    -- معلومات الراتب - Salary Information
    Salary_Total DECIMAL(18, 2),
    Salary_Total_Text NVARCHAR(500),
    Basic_Salary DECIMAL(18, 2),
    Allowances DECIMAL(18, 2),
    
    -- معلومات إضافية - Additional Information
    Age INT,
    Years_Since_Contract_Start INT,
    Remaining_Contract_Renewal INT,
    Skill_level_measurement_certificate INT,
    Training_Hours INT,
    Performance_Score DECIMAL(5, 2),
    Awards INT,
    Gender NVARCHAR(20),
    
    -- الهدف - Target
    promotion_eligible NVARCHAR(10)
);
```

### 3. إدراج بيانات نموذجية (اختياري)

يمكنك استيراد البيانات من ملفات الاختبار:

```bash
# استخدام bcp لاستيراد البيانات
bcp HR_Database.dbo.Employees in test_data/sample_employees.csv -c -t, -S your_server -U your_username -P your_password
```

---

## 🧪 اختبار التدريب من قاعدة البيانات

### 1. من خلال API:

```bash
# التدريب من جدول Employees
curl -X POST "http://localhost:1234/train/from-database?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "Employees",
    "limit": 1000
  }'

# التدريب باستخدام استعلام مخصص
curl -X POST "http://localhost:1234/train/from-database?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM Employees WHERE Dept_Name = '\''IT'\''",
    "limit": 500
  }'
```

### 2. من خلال واجهة الويب:

1. افتح لوحة التحكم: `http://localhost:1234/static/dashboard/index.html`
2. انتقل إلى صفحة "قاعدة البيانات"
3. اختبر الاتصال
4. اختر جدول "Employees"
5. اضغط "تدريب من قاعدة البيانات"

---

## 🔍 استكشاف الأخطاء

### المشكلة 1: لا يزال الخطأ "file not found"

**الحل:**
```bash
# تأكد من إعادة البناء بدون cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# تحقق من التثبيت
docker exec -it hr-ml-system odbcinst -q -d
```

### المشكلة 2: "Login failed for user"

**الحل:**
- تحقق من اسم المستخدم وكلمة المرور في `.env`
- تأكد من أن المستخدم لديه صلاحيات على قاعدة البيانات
- تحقق من أن SQL Server يقبل اتصالات TCP/IP

### المشكلة 3: "Cannot connect to server"

**الحل:**
- تحقق من عنوان Server والمنفذ
- تأكد من أن SQL Server يعمل
- تحقق من إعدادات Firewall
- تأكد من تفعيل TCP/IP في SQL Server Configuration Manager

### المشكلة 4: "Database does not exist"

**الحل:**
- تحقق من اسم قاعدة البيانات في `.env`
- تأكد من أن قاعدة البيانات موجودة في SQL Server
- استخدم SQL Server Management Studio للتحقق

---

## 📊 الأوامر المفيدة

### التحقق من Logs:

```bash
# عرض logs النظام
docker-compose logs -f

# عرض آخر 100 سطر
docker-compose logs --tail=100

# عرض logs لـ container محدد
docker logs hr-ml-system -f
```

### التحقق من ODBC Drivers:

```bash
# الدخول إلى container
docker exec -it hr-ml-system bash

# عرض drivers المثبتة
odbcinst -q -d

# عرض data sources
odbcinst -q -s

# اختبار الاتصال باستخدام sqlcmd
/opt/mssql-tools/bin/sqlcmd -S your_server,1433 -U your_username -P your_password -Q "SELECT @@VERSION"
```

---

## ✅ التحقق من النجاح

بعد إعادة البناء، يجب أن ترى:

### 1. ODBC Driver مثبت:
```bash
$ docker exec -it hr-ml-system odbcinst -q -d
[ODBC Driver 17 for SQL Server]
```

### 2. اختبار الاتصال ناجح:
```json
{
  "success": true,
  "message": "الاتصال بقاعدة البيانات ناجح - Connection successful",
  "server": "your_server",
  "database": "your_database",
  "version": "Microsoft SQL Server 2019..."
}
```

### 3. التدريب من قاعدة البيانات يعمل:
```json
{
  "success": true,
  "message": "تم تدريب النموذج بنجاح",
  "model_type": "RandomForest",
  "accuracy": 0.95,
  "rows_trained": 1000
}
```

---

## 📚 مراجع إضافية

- [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [SQL Server on Linux](https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-overview)

---

## 🎉 الخلاصة

تم إصلاح مشكلة الاتصال بقاعدة البيانات بنجاح! الآن يمكنك:

- ✅ الاتصال بـ SQL Server من Docker container
- ✅ تدريب النماذج مباشرة من قاعدة البيانات
- ✅ استخدام واجهة الويب لإدارة الاتصال
- ✅ الاستفادة من آلية fallback المحسنة

**استمتع باستخدام نظام HR-ML! 🚀**

