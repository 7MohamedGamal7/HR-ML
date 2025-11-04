#!/bin/bash

# اختبار الاتصال بقاعدة البيانات - Test Database Connection
# هذا السكريبت يساعدك في اختبار الاتصال بقاعدة بيانات SQL Server

echo "========================================="
echo "🔧 اختبار الاتصال بقاعدة البيانات"
echo "   Database Connection Test"
echo "========================================="
echo ""

# 1. التحقق من أن Container يعمل
echo "1️⃣ التحقق من Container..."
if docker ps | grep -q hr-ml-system; then
    echo "   ✅ Container يعمل"
else
    echo "   ❌ Container لا يعمل"
    echo "   قم بتشغيله باستخدام: docker-compose up -d"
    exit 1
fi
echo ""

# 2. التحقق من ODBC Driver
echo "2️⃣ التحقق من ODBC Driver..."
DRIVER_CHECK=$(docker exec hr-ml-system odbcinst -q -d 2>/dev/null)
if echo "$DRIVER_CHECK" | grep -q "ODBC Driver 17 for SQL Server"; then
    echo "   ✅ ODBC Driver 17 for SQL Server مثبت"
else
    echo "   ❌ ODBC Driver غير مثبت"
    echo "   قم بإعادة بناء Container: docker-compose build --no-cache"
    exit 1
fi
echo ""

# 3. التحقق من صحة النظام
echo "3️⃣ التحقق من صحة النظام..."
HEALTH_CHECK=$(curl -s http://localhost:1234/health/liveness)
if echo "$HEALTH_CHECK" | grep -q "alive"; then
    echo "   ✅ النظام يعمل بشكل صحيح"
else
    echo "   ❌ النظام لا يستجيب"
    exit 1
fi
echo ""

# 4. طلب معلومات الاتصال من المستخدم
echo "4️⃣ إدخال معلومات الاتصال..."
echo ""

read -p "   أدخل عنوان SQL Server (مثال: 192.168.1.100): " SQL_HOST
read -p "   أدخل المنفذ (افتراضي: 1433): " SQL_PORT
SQL_PORT=${SQL_PORT:-1433}
read -p "   أدخل اسم قاعدة البيانات: " SQL_DATABASE
read -p "   أدخل اسم المستخدم: " SQL_USERNAME
read -sp "   أدخل كلمة المرور: " SQL_PASSWORD
echo ""
echo ""

# 5. اختبار الاتصال
echo "5️⃣ اختبار الاتصال..."
echo ""

# إنشاء ملف .env مؤقت
cat > .env.test << EOF
SQL_SERVER_HOST=$SQL_HOST
SQL_SERVER_PORT=$SQL_PORT
SQL_SERVER_DATABASE=$SQL_DATABASE
SQL_SERVER_USERNAME=$SQL_USERNAME
SQL_SERVER_PASSWORD=$SQL_PASSWORD
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_TIMEOUT=30
DEFAULT_EMPLOYEE_TABLE=Employees
EOF

# تحديث متغيرات البيئة في Container
docker exec hr-ml-system bash -c "
export SQL_SERVER_HOST='$SQL_HOST'
export SQL_SERVER_PORT='$SQL_PORT'
export SQL_SERVER_DATABASE='$SQL_DATABASE'
export SQL_SERVER_USERNAME='$SQL_USERNAME'
export SQL_SERVER_PASSWORD='$SQL_PASSWORD'
"

# اختبار الاتصال عبر API
echo "   جاري الاتصال بـ $SQL_HOST:$SQL_PORT/$SQL_DATABASE..."
echo ""

RESULT=$(curl -s -X GET "http://localhost:1234/train/database/test-connection?lang=ar")

# عرض النتيجة
if echo "$RESULT" | grep -q '"success":true'; then
    echo "   ✅✅✅ نجح الاتصال بقاعدة البيانات! ✅✅✅"
    echo ""
    echo "   📊 معلومات الاتصال:"
    echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
    echo ""
    echo "========================================="
    echo "🎉 تم الاتصال بنجاح!"
    echo "========================================="
    echo ""
    echo "الخطوات التالية:"
    echo "1. قم بتحديث ملف .env بمعلومات الاتصال"
    echo "2. أعد تشغيل Container: docker-compose restart"
    echo "3. افتح لوحة التحكم: http://localhost:1234/static/dashboard/index.html"
    echo "4. انتقل إلى صفحة 'قاعدة البيانات' وابدأ التدريب"
    echo ""
    
    # حفظ الإعدادات في .env
    read -p "هل تريد حفظ هذه الإعدادات في ملف .env؟ (y/n): " SAVE_ENV
    if [ "$SAVE_ENV" = "y" ] || [ "$SAVE_ENV" = "Y" ]; then
        cp .env.test .env
        echo "✅ تم حفظ الإعدادات في .env"
        echo "⚠️  قم بإعادة تشغيل Container: docker-compose restart"
    fi
    
else
    echo "   ❌❌❌ فشل الاتصال بقاعدة البيانات ❌❌❌"
    echo ""
    echo "   📋 تفاصيل الخطأ:"
    echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
    echo ""
    echo "========================================="
    echo "🔍 استكشاف الأخطاء:"
    echo "========================================="
    echo ""
    echo "1. تحقق من عنوان Server والمنفذ"
    echo "2. تحقق من اسم المستخدم وكلمة المرور"
    echo "3. تأكد من أن SQL Server يقبل اتصالات TCP/IP"
    echo "4. تحقق من إعدادات Firewall"
    echo "5. راجع ملف DATABASE_CONNECTION_FIX.md للمزيد من المساعدة"
    echo ""
fi

# تنظيف
rm -f .env.test

echo ""
echo "========================================="
echo "انتهى الاختبار"
echo "========================================="

