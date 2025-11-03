# 📘 دليل الاتصال بقاعدة بيانات SQL Server
# SQL Server Database Connection Guide

---

## 📋 **المحتويات - Table of Contents**

1. [المتطلبات الأساسية](#المتطلبات-الأساسية)
2. [تثبيت ODBC Driver](#تثبيت-odbc-driver)
3. [إعداد قاعدة البيانات](#إعداد-قاعدة-البيانات)
4. [تكوين الاتصال](#تكوين-الاتصال)
5. [اختبار الاتصال](#اختبار-الاتصال)
6. [التدريب من قاعدة البيانات](#التدريب-من-قاعدة-البيانات)
7. [حل المشاكل الشائعة](#حل-المشاكل-الشائعة)

---

## 🔧 **المتطلبات الأساسية - Prerequisites**

### **1. SQL Server**
- SQL Server 2012 أو أحدث
- يمكن استخدام:
  - SQL Server Express (مجاني)
  - SQL Server Developer Edition (مجاني)
  - SQL Server Standard/Enterprise

### **2. Python Libraries**
تم تثبيتها تلقائياً مع النظام:
```bash
pyodbc>=5.0.0
sqlalchemy>=2.0.0
pymssql>=2.2.0
```

---

## 📥 **تثبيت ODBC Driver**

### **Windows:**

1. **تحميل ODBC Driver 17 for SQL Server:**
   - زيارة: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
   - تحميل وتثبيت "ODBC Driver 17 for SQL Server"

2. **التحقق من التثبيت:**
   ```powershell
   # فتح ODBC Data Source Administrator
   odbcad32
   ```
   - تحقق من وجود "ODBC Driver 17 for SQL Server" في قائمة Drivers

### **Linux (Ubuntu/Debian):**

```bash
# إضافة Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# تحديث وتثبيت
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# تثبيت أدوات إضافية (اختياري)
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc

# تثبيت unixODBC development headers
sudo apt-get install -y unixodbc-dev
```

### **Linux (CentOS/RHEL):**

```bash
# إضافة Microsoft repository
sudo curl -o /etc/yum.repos.d/mssql-release.repo https://packages.microsoft.com/config/rhel/8/prod.repo

# تثبيت
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel
sudo ACCEPT_EULA=Y yum install -y msodbcsql17

# تثبيت أدوات إضافية (اختياري)
sudo ACCEPT_EULA=Y yum install -y mssql-tools
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc

# تثبيت unixODBC development headers
sudo yum install -y unixODBC-devel
```

### **macOS:**

```bash
# تثبيت Homebrew إذا لم يكن مثبتاً
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# تثبيت ODBC Driver
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

---

## 🗄️ **إعداد قاعدة البيانات - Database Setup**

### **1. إنشاء قاعدة البيانات:**

```sql
-- إنشاء قاعدة بيانات جديدة
CREATE DATABASE HR_Database;
GO

USE HR_Database;
GO
```

### **2. إنشاء جدول الموظفين:**

```sql
-- إنشاء جدول الموظفين بجميع الأعمدة المطلوبة
CREATE TABLE Employees (
    -- معلومات أساسية - Basic Information
    Emp_ID INT PRIMARY KEY IDENTITY(1,1),
    Emp_Full_Name NVARCHAR(200),
    Emp_Phone1 NVARCHAR(20),
    Emp_Address NVARCHAR(500),
    National_ID NVARCHAR(20),
    Date_Birth DATE,
    Place_Birth NVARCHAR(100),
    
    -- معلومات العمل - Employment Information
    Emp_Type NVARCHAR(50),
    Working_Condition NVARCHAR(50),
    Dept_Name NVARCHAR(100),
    Jop_Name NVARCHAR(100),
    Emp_Date_Hiring DATE,
    
    -- معلومات شخصية - Personal Information
    Emp_Marital_Status NVARCHAR(20),
    Emp_Nationality NVARCHAR(50),
    People_With_Special_Needs BIT DEFAULT 0,
    gender NVARCHAR(10),
    Governorate NVARCHAR(50),
    
    -- معلومات الراتب - Salary Information
    Salary_Total DECIMAL(18,2),
    Basic_Salary DECIMAL(18,2),
    Allowances DECIMAL(18,2),
    Insurance_Salary DECIMAL(18,2),
    
    -- معلومات التأمين - Insurance Information
    Insurance_Status NVARCHAR(50),
    Jop_Code_insurance NVARCHAR(50),
    Jop_Name_insurance NVARCHAR(100),
    Number_Insurance NVARCHAR(50),
    Date_Insurance_Start DATE,
    Percentage_Insurance_Payable DECIMAL(5,2),
    Due_Insurance_Amount DECIMAL(18,2),
    
    -- معلومات الصحة - Health Information
    Health_Card NVARCHAR(50),
    Health_Card_Expiration_Date DATE,
    
    -- معلومات النقل - Transportation Information
    Emp_Car BIT DEFAULT 0,
    Car_Ride_Time INT,
    Car_Pick_Up_Point NVARCHAR(200),
    Shift_Type NVARCHAR(50),
    
    -- معلومات الأداء - Performance Information
    Training_Hours DECIMAL(10,2) DEFAULT 0,
    Performance_Score DECIMAL(5,2) DEFAULT 50,
    Awards INT DEFAULT 0,
    Skill_level_measurement_certificate INT DEFAULT 0,
    
    -- معلومات العقد - Contract Information
    Remaining_Contract_Renewal INT DEFAULT 12,
    
    -- أعمدة محسوبة - Calculated Columns
    Age AS (DATEDIFF(YEAR, Date_Birth, GETDATE())),
    Years_Since_Contract_Start AS (DATEDIFF(YEAR, Emp_Date_Hiring, GETDATE()))
);
GO
```

### **3. إدخال بيانات تجريبية:**

```sql
-- إدخال بيانات تجريبية
INSERT INTO Employees (
    Emp_Full_Name, Emp_Phone1, National_ID, Date_Birth, 
    Emp_Type, Working_Condition, Dept_Name, Jop_Name, Emp_Date_Hiring,
    Emp_Marital_Status, Emp_Nationality, gender, Governorate,
    Salary_Total, Basic_Salary, Allowances, Insurance_Salary,
    Training_Hours, Performance_Score, Awards, Shift_Type
)
VALUES
    (N'أحمد محمد علي', '01012345678', '29001011234567', '1990-01-01', 
     N'دائم', N'موظف', N'تكنولوجيا المعلومات', N'مبرمج', '2018-03-15',
     N'متزوج', N'مصري', 'male', N'القاهرة',
     8000, 6000, 2000, 6000,
     40, 85, 2, N'صباحي'),
    
    (N'فاطمة حسن محمود', '01098765432', '29101011234568', '1991-10-10', 
     N'دائم', N'موظف', N'الموارد البشرية', N'أخصائي موارد بشرية', '2019-06-20',
     N'أعزب', N'مصري', 'female', N'الجيزة',
     7000, 5500, 1500, 5500,
     35, 78, 1, N'صباحي'),
    
    (N'محمود سعيد أحمد', '01123456789', '29202011234569', '1992-02-20', 
     N'مؤقت', N'متعاقد', N'المبيعات', N'مندوب مبيعات', '2020-01-10',
     N'متزوج', N'مصري', 'male', N'الإسكندرية',
     6000, 4500, 1500, 4500,
     20, 65, 0, N'مسائي');
GO
```

### **4. إنشاء مستخدم للنظام:**

```sql
-- إنشاء login
CREATE LOGIN hr_system_user WITH PASSWORD = 'YourStrongPassword123!';
GO

-- إنشاء user في قاعدة البيانات
USE HR_Database;
GO
CREATE USER hr_system_user FOR LOGIN hr_system_user;
GO

-- منح الصلاحيات
GRANT SELECT, INSERT, UPDATE ON Employees TO hr_system_user;
GO
```

---

## ⚙️ **تكوين الاتصال - Connection Configuration**

### **1. إنشاء ملف `.env`:**

```bash
# نسخ ملف المثال
cp .env.example .env
```

### **2. تحديث إعدادات SQL Server في `.env`:**

```bash
# إعدادات SQL Server - SQL Server Configuration
SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=hr_system_user
SQL_SERVER_PASSWORD=YourStrongPassword123!
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_TIMEOUT=30
DEFAULT_EMPLOYEE_TABLE=Employees
```

### **3. للاتصال بـ SQL Server على جهاز آخر:**

```bash
# استبدل localhost بعنوان IP أو اسم الخادم
SQL_SERVER_HOST=192.168.1.100
# أو
SQL_SERVER_HOST=sql-server.company.com
```

---

## ✅ **اختبار الاتصال - Testing Connection**

### **1. باستخدام API:**

```bash
# اختبار الاتصال
curl -X GET "http://localhost:1234/train/database/test-connection?lang=ar"
```

**النتيجة المتوقعة:**
```json
{
  "detail": "الاتصال بقاعدة البيانات ناجح - Database connection successful",
  "connection_info": {
    "success": true,
    "server": "localhost",
    "database": "HR_Database",
    "driver": "ODBC Driver 17 for SQL Server"
  }
}
```

### **2. الحصول على قائمة الجداول:**

```bash
curl -X GET "http://localhost:1234/train/database/tables?lang=ar"
```

### **3. الحصول على معلومات جدول:**

```bash
curl -X GET "http://localhost:1234/train/database/table-info?table_name=Employees&lang=ar"
```

---

## 🎓 **التدريب من قاعدة البيانات - Training from Database**

### **1. التدريب على جميع البيانات:**

```bash
curl -X POST "http://localhost:1234/train/from-database?lang=ar" \
  -H "Content-Type: application/json"
```

### **2. التدريب على جدول محدد:**

```bash
curl -X POST "http://localhost:1234/train/from-database?table_name=Employees&lang=ar" \
  -H "Content-Type: application/json"
```

### **3. التدريب مع حد لعدد الصفوف:**

```bash
curl -X POST "http://localhost:1234/train/from-database?table_name=Employees&limit=1000&lang=ar" \
  -H "Content-Type: application/json"
```

### **4. التدريب باستخدام استعلام SQL مخصص:**

```bash
curl -X POST "http://localhost:1234/train/from-database?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM Employees WHERE Dept_Name = N'\''تكنولوجيا المعلومات'\''"
  }'
```

---

## 🔧 **حل المشاكل الشائعة - Troubleshooting**

### **❌ مشكلة: "ODBC Driver not found"**

**الحل:**
```bash
# Windows: تثبيت ODBC Driver 17
# تحميل من: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Linux: تثبيت msodbcsql17
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### **❌ مشكلة: "Login failed for user"**

**الحل:**
1. تحقق من اسم المستخدم وكلمة المرور في `.env`
2. تأكد من أن المستخدم لديه صلاحيات على قاعدة البيانات:
```sql
USE HR_Database;
GRANT SELECT ON Employees TO hr_system_user;
```

### **❌ مشكلة: "Cannot connect to server"**

**الحل:**
1. تحقق من أن SQL Server يعمل
2. تحقق من تفعيل TCP/IP في SQL Server Configuration Manager
3. تحقق من Firewall:
```bash
# Windows: السماح بالمنفذ 1433
netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433
```

### **❌ مشكلة: "Table 'Employees' not found"**

**الحل:**
```sql
-- التحقق من وجود الجدول
USE HR_Database;
SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Employees';

-- إنشاء الجدول إذا لم يكن موجوداً
-- (استخدم الكود من قسم "إعداد قاعدة البيانات")
```

---

## 📊 **مثال كامل - Complete Example**

```bash
# 1. اختبار الاتصال
curl -X GET "http://localhost:1234/train/database/test-connection?lang=ar"

# 2. الحصول على قائمة الجداول
curl -X GET "http://localhost:1234/train/database/tables?lang=ar"

# 3. الحصول على معلومات جدول الموظفين
curl -X GET "http://localhost:1234/train/database/table-info?table_name=Employees&lang=ar"

# 4. التدريب من قاعدة البيانات
curl -X POST "http://localhost:1234/train/from-database?table_name=Employees&lang=ar"

# 5. التنبؤ لموظف جديد
curl -X POST "http://localhost:1234/predict/?lang=ar" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

## 🎉 **تم بنجاح!**

الآن يمكنك:
- ✅ الاتصال بقاعدة بيانات SQL Server
- ✅ تحميل بيانات الموظفين من قاعدة البيانات
- ✅ تدريب النموذج على البيانات الحقيقية
- ✅ التنبؤ بالترقيات للموظفين

---

## 📞 **الدعم - Support**

إذا واجهت أي مشاكل:
1. راجع قسم "حل المشاكل الشائعة"
2. تحقق من ملف `logs/app.log` للحصول على تفاصيل الأخطاء
3. تأكد من تثبيت جميع المتطلبات بشكل صحيح

