# 📘 الدليل الشامل للاتصال بـ SQL Server - Complete SQL Server Connection Guide

## 🎯 نظرة عامة - Overview

هذا الدليل الشامل يغطي جميع جوانب الاتصال بـ SQL Server من نظام HR-ML الذي يعمل في Docker.

This comprehensive guide covers all aspects of connecting to SQL Server from the HR-ML system running in Docker.

---

## 📋 جدول المحتويات - Table of Contents

1. [السيناريوهات المختلفة - Different Scenarios](#scenarios)
2. [الإعداد السريع - Quick Setup](#quick-setup)
3. [استكشاف الأخطاء - Troubleshooting](#troubleshooting)
4. [الأسئلة الشائعة - FAQ](#faq)
5. [الأدوات المتاحة - Available Tools](#tools)

---

<a name="scenarios"></a>
## 🎭 السيناريوهات المختلفة - Different Scenarios

### السيناريو 1: SQL Server محلي على Windows/Mac
**Local SQL Server on Windows/Mac**

#### الإعدادات:
```env
SQL_SERVER_HOST=host.docker.internal
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourPassword123!
SQL_SERVER_TIMEOUT=60
```

#### ⚠️ ملاحظات مهمة:
- **لا تستخدم** `localhost` أو `127.0.0.1` أو `(local)`
- **استخدم** `host.docker.internal` فقط
- السبب: Docker container يعمل في شبكة منفصلة

#### خطوات التحقق:
1. تأكد من أن SQL Server يعمل:
   ```powershell
   Get-Service -Name 'MSSQL*'
   ```

2. تأكد من تفعيل TCP/IP:
   - افتح SQL Server Configuration Manager
   - انتقل إلى: SQL Server Network Configuration → Protocols
   - تأكد من أن TCP/IP = Enabled

3. تأكد من فتح المنفذ 1433:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 1433
   ```

4. أضف قاعدة Firewall:
   ```powershell
   New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
   ```

---

### السيناريو 2: SQL Server على جهاز آخر في الشبكة
**SQL Server on Another Machine in the Network**

#### الإعدادات:
```env
SQL_SERVER_HOST=192.168.1.50
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourPassword123!
SQL_SERVER_TIMEOUT=60
```

#### خطوات التحقق:
1. احصل على عنوان IP للجهاز البعيد:
   ```cmd
   ipconfig
   ```

2. اختبر الاتصال من جهازك:
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.50 -Port 1433
   ```

3. تأكد من إعدادات Firewall على الجهاز البعيد

4. تأكد من أن SQL Server يقبل اتصالات بعيدة:
   - SQL Server Properties → Connections
   - Allow remote connections = Checked

---

### السيناريو 3: SQL Server Express (Named Instance)
**SQL Server Express with Named Instance**

#### الإعدادات:
```env
SQL_SERVER_HOST=host.docker.internal\\SQLEXPRESS
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourPassword123!
SQL_SERVER_TIMEOUT=60
```

#### ⚠️ ملاحظات مهمة:
- استخدم `\\` للـ backslash في Named Instance
- تأكد من تشغيل SQL Server Browser:
  ```powershell
  Get-Service -Name 'SQLBrowser'
  Start-Service -Name 'SQLBrowser'
  ```

---

<a name="quick-setup"></a>
## 🚀 الإعداد السريع - Quick Setup

### الطريقة 1: استخدام أداة التشخيص التفاعلية (الأسهل!)

```bash
bash diagnose_sql_connection.sh
```

الأداة ستقوم بـ:
- ✅ فحص Docker و ODBC Driver
- ✅ طلب معلومات الاتصال
- ✅ اختبار الاتصال من Host ومن Docker
- ✅ تقديم توصيات تلقائية
- ✅ إنشاء ملف `.env` جاهز

### الطريقة 2: استخدام واجهة الويب

1. افتح لوحة التحكم:
   ```
   http://localhost:1234/static/dashboard/index.html
   ```

2. انتقل إلى صفحة "قاعدة البيانات"

3. أدخل معلومات الاتصال

4. اضغط "تشخيص المشكلة" للحصول على تقرير شامل

5. اضغط "اختبار الاتصال" للتحقق

### الطريقة 3: يدوياً

1. انسخ ملف `.env.example` إلى `.env`:
   ```bash
   cp .env.example .env
   ```

2. حدّث الإعدادات في `.env`

3. أعد تشغيل Docker:
   ```bash
   docker-compose restart
   ```

4. اختبر الاتصال:
   ```bash
   curl -X GET "http://localhost:1234/train/database/test-connection?lang=ar"
   ```

---

<a name="troubleshooting"></a>
## 🔍 استكشاف الأخطاء - Troubleshooting

### الخطأ 1: Login timeout expired (HYT00)

**الأسباب:**
- عنوان Server خاطئ
- استخدام `localhost` بدلاً من `host.docker.internal`
- TCP/IP غير مفعّل
- Firewall يحجب المنفذ

**الحلول:**
1. استخدم `host.docker.internal` للـ Local SQL Server
2. فعّل TCP/IP في SQL Server Configuration Manager
3. أضف قاعدة Firewall للمنفذ 1433
4. زد قيمة Timeout إلى 60 ثانية

### الخطأ 2: Login failed for user (28000)

**الأسباب:**
- اسم المستخدم أو كلمة المرور خاطئة
- SQL Server Authentication غير مفعّل
- المستخدم ليس لديه صلاحيات

**الحلول:**
1. تحقق من Username/Password
2. فعّل SQL Server Authentication:
   - Server Properties → Security
   - SQL Server and Windows Authentication mode
3. امنح المستخدم صلاحيات على قاعدة البيانات

### الخطأ 3: Cannot open database (42000)

**الأسباب:**
- اسم قاعدة البيانات خاطئ
- قاعدة البيانات غير موجودة
- المستخدم ليس لديه صلاحيات

**الحلول:**
1. تحقق من اسم قاعدة البيانات في SSMS
2. تأكد من وجود قاعدة البيانات
3. امنح المستخدم صلاحيات:
   ```sql
   USE HR_Database;
   CREATE USER [sa] FOR LOGIN [sa];
   ALTER ROLE db_owner ADD MEMBER [sa];
   ```

### الخطأ 4: A network-related error (08001)

**الأسباب:**
- SQL Server لا يعمل
- عنوان Server خاطئ
- مشاكل في الشبكة

**الحلول:**
1. تأكد من أن SQL Server يعمل:
   ```powershell
   Get-Service -Name 'MSSQL*' | Start-Service
   ```
2. تحقق من عنوان Server
3. اختبر الاتصال بالشبكة

---

<a name="faq"></a>
## ❓ الأسئلة الشائعة - FAQ

### Q1: لماذا لا يعمل localhost؟
**A:** Docker container يعمل في شبكة منفصلة. `localhost` يشير إلى Container نفسه وليس الجهاز المضيف. استخدم `host.docker.internal` بدلاً منه.

### Q2: كيف أعرف عنوان IP لجهازي؟
**A:** استخدم:
```powershell
ipconfig
```
ابحث عن IPv4 Address في قسم Ethernet أو Wi-Fi.

### Q3: كيف أتحقق من أن SQL Server يعمل؟
**A:** استخدم:
```powershell
Get-Service -Name 'MSSQL*'
```
يجب أن يكون Status = Running.

### Q4: كيف أفعّل TCP/IP؟
**A:**
1. افتح SQL Server Configuration Manager
2. SQL Server Network Configuration → Protocols for [Instance]
3. انقر بزر الماوس الأيمن على TCP/IP → Enable
4. أعد تشغيل SQL Server

### Q5: كيف أفتح المنفذ 1433 في Firewall؟
**A:** استخدم PowerShell كمسؤول:
```powershell
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
```

### Q6: كيف أغيّر Timeout؟
**A:** في ملف `.env`:
```env
SQL_SERVER_TIMEOUT=60
```
ثم أعد تشغيل: `docker-compose restart`

### Q7: كيف أختبر الاتصال من خارج Docker؟
**A:** استخدم SSMS أو:
```powershell
Test-NetConnection -ComputerName localhost -Port 1433
```

### Q8: ماذا لو كان SQL Server على منفذ مختلف؟
**A:** حدّث `.env`:
```env
SQL_SERVER_PORT=1434
```

### Q9: كيف أعرف أي ODBC Drivers مثبتة؟
**A:**
```bash
docker exec hr-ml-system odbcinst -q -d
```

### Q10: كيف أحصل على تقرير تشخيصي شامل؟
**A:** استخدم:
```bash
bash diagnose_sql_connection.sh
```
أو من واجهة الويب: اضغط "تشخيص المشكلة"

---

<a name="tools"></a>
## 🛠️ الأدوات المتاحة - Available Tools

### 1. أداة التشخيص التفاعلية
```bash
bash diagnose_sql_connection.sh
```
- فحص شامل تلقائي
- توصيات مخصصة
- إنشاء ملف `.env` جاهز

### 2. سكريبت اختبار الاتصال
```bash
bash test_database_connection.sh
```
- اختبار سريع
- حفظ الإعدادات

### 3. API Endpoints

#### اختبار الاتصال:
```bash
curl -X GET "http://localhost:1234/train/database/test-connection?lang=ar"
```

#### التشخيص الشامل:
```bash
curl -X GET "http://localhost:1234/train/database/diagnose?lang=ar"
```

#### عرض الجداول:
```bash
curl -X GET "http://localhost:1234/train/database/tables?lang=ar"
```

### 4. واجهة الويب

#### لوحة التحكم:
```
http://localhost:1234/static/dashboard/index.html
```

#### صفحة قاعدة البيانات:
```
http://localhost:1234/static/database_connection.html
```

#### Swagger API:
```
http://localhost:1234/docs
```

---

## 📚 ملفات التوثيق الإضافية

1. **`SQL_SERVER_TIMEOUT_TROUBLESHOOTING.md`** - دليل حل مشكلة Timeout
2. **`DATABASE_FIX_SUMMARY.md`** - ملخص إصلاح ODBC Driver
3. **`QUICK_START_DATABASE.md`** - دليل البدء السريع
4. **`DATABASE_CONNECTION_FIX.md`** - دليل تفصيلي للإصلاحات

---

## 🎯 خطوات النجاح المضمونة

### للمبتدئين:

1. **استخدم أداة التشخيص:**
   ```bash
   bash diagnose_sql_connection.sh
   ```

2. **اتبع التوصيات** التي تظهر

3. **انسخ الإعدادات:**
   ```bash
   cp .env.diagnostic .env
   ```

4. **أعد التشغيل:**
   ```bash
   docker-compose restart
   ```

### للمتقدمين:

1. **تحقق من الإعدادات يدوياً**
2. **اختبر من Host أولاً**
3. **اختبر من Docker ثانياً**
4. **راجع Logs:**
   ```bash
   docker-compose logs -f
   ```

---

## 🆘 الحصول على المساعدة

إذا جربت كل شيء ولم ينجح:

1. **شغّل أداة التشخيص** واحفظ التقرير
2. **راجع Logs:**
   ```bash
   docker-compose logs --tail=100
   ```
3. **تحقق من:**
   - SQL Server يعمل
   - TCP/IP مفعّل
   - Firewall مفتوح
   - الإعدادات صحيحة

---

**🎊 بالتوفيق! نظام HR-ML جاهز للاتصال بـ SQL Server! 🚀**

