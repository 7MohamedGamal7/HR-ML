# 🔍 دليل حل مشكلة Timeout في الاتصال بـ SQL Server

## ❌ المشكلة

```
فشل الاتصال بقاعدة البيانات - Connection failed: 
('HYT00', '[HYT00] [Microsoft][ODBC Driver 17 for SQL Server]Login timeout expired (0) (SQLDriverConnect)')
```

**نوع الخطأ:** HYT00 - Login Timeout Expired  
**المعنى:** النظام لم يستطع الاتصال بـ SQL Server خلال المدة المحددة (30 ثانية)

---

## 🎯 الأسباب المحتملة

### 1. **عنوان Server خاطئ** ⚠️
- عنوان IP غير صحيح
- اسم Server خاطئ
- Server غير موجود على الشبكة

### 2. **SQL Server لا يقبل اتصالات TCP/IP** 🔌
- TCP/IP غير مفعّل في SQL Server Configuration Manager
- SQL Server يعمل فقط على Named Pipes

### 3. **Firewall يحجب الاتصال** 🛡️
- Windows Firewall يحجب المنفذ 1433
- Firewall الشبكة يحجب الاتصال
- Antivirus يحجب الاتصال

### 4. **المنفذ (Port) خاطئ** 🔢
- SQL Server يعمل على منفذ مختلف عن 1433
- Dynamic Port بدلاً من Static Port

### 5. **SQL Server لا يعمل** 🔴
- خدمة SQL Server متوقفة
- SQL Server Browser متوقف

### 6. **مشاكل الشبكة** 🌐
- Docker لا يستطيع الوصول إلى الشبكة الخارجية
- مشاكل DNS
- مشاكل في الـ Network Mode في Docker

---

## 🔧 خطوات التشخيص والحل

### **الخطوة 1: تحديد موقع SQL Server** 📍

#### أ. SQL Server على نفس الجهاز (Local)

إذا كان SQL Server على نفس الجهاز الذي يعمل عليه Docker:

**❌ لا تستخدم:**
- `localhost`
- `127.0.0.1`
- `(local)`

**✅ استخدم:**
- `host.docker.internal` (على Windows/Mac)
- عنوان IP الفعلي للجهاز (مثال: `192.168.1.100`)

**السبب:** Docker container يعمل في شبكة منفصلة، `localhost` يشير إلى Container نفسه وليس الجهاز المضيف.

#### ب. SQL Server على جهاز آخر (Remote)

استخدم:
- عنوان IP للجهاز (مثال: `192.168.1.50`)
- اسم الجهاز على الشبكة (مثال: `SERVER-PC`)

---

### **الخطوة 2: التحقق من SQL Server Configuration** ⚙️

#### 1. تفعيل TCP/IP Protocol

1. افتح **SQL Server Configuration Manager**
2. انتقل إلى: **SQL Server Network Configuration** → **Protocols for [Instance Name]**
3. تأكد من أن **TCP/IP** = **Enabled**
4. إذا كان Disabled، قم بتفعيله
5. أعد تشغيل خدمة SQL Server

#### 2. التحقق من Port Number

1. في SQL Server Configuration Manager
2. انقر بزر الماوس الأيمن على **TCP/IP** → **Properties**
3. انتقل إلى تبويب **IP Addresses**
4. ابحث عن **IPAll** في الأسفل
5. تحقق من:
   - **TCP Dynamic Ports:** يجب أن يكون **فارغاً**
   - **TCP Port:** يجب أن يكون **1433**
6. إذا كان مختلفاً، قم بتعديله
7. أعد تشغيل خدمة SQL Server

#### 3. تفعيل SQL Server Browser (للـ Named Instances)

إذا كنت تستخدم Named Instance (مثل `SQLEXPRESS`):

1. افتح **SQL Server Configuration Manager**
2. انتقل إلى **SQL Server Services**
3. ابحث عن **SQL Server Browser**
4. تأكد من أنه **Running**
5. اضبط Startup Type على **Automatic**

---

### **الخطوة 3: إعداد Windows Firewall** 🛡️

#### السماح بالمنفذ 1433

**PowerShell (كمسؤول):**
```powershell
# السماح بالمنفذ 1433
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow

# السماح بـ SQL Server Browser (UDP 1434)
New-NetFirewallRule -DisplayName "SQL Server Browser" -Direction Inbound -Protocol UDP -LocalPort 1434 -Action Allow
```

**أو يدوياً:**
1. افتح **Windows Defender Firewall**
2. اضغط **Advanced Settings**
3. اضغط **Inbound Rules** → **New Rule**
4. اختر **Port** → **Next**
5. اختر **TCP** وأدخل **1433** → **Next**
6. اختر **Allow the connection** → **Next**
7. اختر جميع الـ Profiles → **Next**
8. أدخل اسم: **SQL Server Port 1433** → **Finish**

---

### **الخطوة 4: التحقق من SQL Server Authentication** 🔐

1. افتح **SQL Server Management Studio (SSMS)**
2. اتصل بـ SQL Server
3. انقر بزر الماوس الأيمن على Server → **Properties**
4. انتقل إلى **Security**
5. تأكد من اختيار: **SQL Server and Windows Authentication mode**
6. اضغط **OK**
7. أعد تشغيل خدمة SQL Server

---

### **الخطوة 5: اختبار الاتصال من خارج Docker** 🧪

#### أ. اختبار باستخدام SSMS

1. افتح **SQL Server Management Studio**
2. في Server name، أدخل: `your_server_ip,1433`
3. اختر **SQL Server Authentication**
4. أدخل Username و Password
5. اضغط **Connect**

إذا نجح الاتصال، المشكلة في Docker. إذا فشل، المشكلة في SQL Server نفسه.

#### ب. اختبار باستخدام telnet

```cmd
telnet your_server_ip 1433
```

إذا اتصل، المنفذ مفتوح. إذا فشل، المنفذ محجوب أو SQL Server لا يعمل.

#### ج. اختبار باستخدام PowerShell

```powershell
Test-NetConnection -ComputerName your_server_ip -Port 1433
```

---

### **الخطوة 6: إصلاح Docker Network** 🐳

#### أ. استخدام host.docker.internal (للـ Local SQL Server)

حدّث ملف `.env`:
```env
SQL_SERVER_HOST=host.docker.internal
SQL_SERVER_PORT=1433
```

#### ب. استخدام Network Mode: host (Linux فقط)

في `docker-compose.yml`:
```yaml
services:
  hr-system:
    network_mode: "host"
```

**ملاحظة:** هذا لا يعمل على Windows/Mac.

#### ج. التحقق من Docker Network

```bash
# عرض الشبكات
docker network ls

# فحص الشبكة
docker network inspect hr-model_hr-network
```

---

### **الخطوة 7: زيادة Timeout** ⏱️

إذا كان الاتصال بطيئاً، قم بزيادة Timeout:

حدّث ملف `.env`:
```env
SQL_SERVER_TIMEOUT=60
```

أو في الكود مباشرة في `app/config.py`:
```python
SQL_SERVER_TIMEOUT = int(os.getenv("SQL_SERVER_TIMEOUT", "60"))
```

---

## 🛠️ أداة التشخيص التلقائي

استخدم السكريبت التشخيصي:

```bash
bash diagnose_sql_connection.sh
```

السكريبت سيقوم بـ:
1. ✅ التحقق من Docker
2. ✅ التحقق من ODBC Driver
3. ✅ اختبار الاتصال بـ SQL Server من الجهاز المضيف
4. ✅ اختبار الاتصال من داخل Docker Container
5. ✅ فحص Firewall
6. ✅ فحص SQL Server Configuration
7. ✅ تقديم توصيات للحل

---

## 📋 حلول سريعة حسب السيناريو

### **السيناريو 1: SQL Server على نفس الجهاز (Windows)**

```env
SQL_SERVER_HOST=host.docker.internal
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourPassword123!
SQL_SERVER_TIMEOUT=60
```

### **السيناريو 2: SQL Server على جهاز آخر**

```env
SQL_SERVER_HOST=192.168.1.50
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourPassword123!
SQL_SERVER_TIMEOUT=60
```

### **السيناريو 3: SQL Server Express (Named Instance)**

```env
SQL_SERVER_HOST=host.docker.internal\\SQLEXPRESS
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=HR_Database
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourPassword123!
SQL_SERVER_TIMEOUT=60
```

**ملاحظة:** استخدم `\\` للـ backslash في Named Instance.

---

## 🔍 الأخطاء الشائعة وحلولها

### ❌ "Login timeout expired"
**الحل:** تحقق من عنوان Server، تأكد من تفعيل TCP/IP، تحقق من Firewall

### ❌ "Cannot open database"
**الحل:** تحقق من اسم Database، تأكد من أن المستخدم لديه صلاحيات

### ❌ "Login failed for user"
**الحل:** تحقق من Username/Password، تأكد من تفعيل SQL Server Authentication

### ❌ "A network-related or instance-specific error"
**الحل:** تحقق من أن SQL Server يعمل، تحقق من اسم Server

---

## 📞 الخطوات التالية

بعد حل المشكلة:

1. ✅ حدّث ملف `.env` بالإعدادات الصحيحة
2. ✅ أعد تشغيل Docker: `docker-compose restart`
3. ✅ اختبر الاتصال: `bash test_database_connection.sh`
4. ✅ ابدأ التدريب من لوحة التحكم

---

**🎯 في 90% من الحالات، المشكلة هي:**
1. استخدام `localhost` بدلاً من `host.docker.internal`
2. TCP/IP غير مفعّل في SQL Server
3. Firewall يحجب المنفذ 1433

**جرب هذه الحلول أولاً!** ✨

