#!/bin/bash

# أداة تشخيص الاتصال بـ SQL Server - SQL Server Connection Diagnostic Tool
# تقوم بفحص شامل لمشاكل الاتصال وتقديم حلول تلقائية

# الألوان - Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# رموز - Icons
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
WRENCH="🔧"
MAGNIFY="🔍"

echo ""
echo "========================================="
echo -e "${CYAN}${MAGNIFY} أداة تشخيص الاتصال بـ SQL Server${NC}"
echo -e "${CYAN}   SQL Server Connection Diagnostic Tool${NC}"
echo "========================================="
echo ""

# متغيرات عامة
ISSUES_FOUND=0
RECOMMENDATIONS=()

# وظيفة لإضافة توصية
add_recommendation() {
    RECOMMENDATIONS+=("$1")
}

# وظيفة لعرض التوصيات
show_recommendations() {
    if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
        echo ""
        echo "========================================="
        echo -e "${YELLOW}${WRENCH} التوصيات المقترحة - Recommendations${NC}"
        echo "========================================="
        for i in "${!RECOMMENDATIONS[@]}"; do
            echo -e "${YELLOW}$((i+1)). ${RECOMMENDATIONS[$i]}${NC}"
        done
        echo ""
    fi
}

# 1. التحقق من Docker
echo -e "${BLUE}[1/8]${NC} ${INFO} التحقق من Docker - Checking Docker..."
if docker ps &> /dev/null; then
    if docker ps | grep -q hr-ml-system; then
        echo -e "      ${GREEN}${CHECK} Container hr-ml-system يعمل${NC}"
    else
        echo -e "      ${RED}${CROSS} Container hr-ml-system لا يعمل${NC}"
        echo -e "      ${YELLOW}قم بتشغيله: docker-compose up -d${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        add_recommendation "قم بتشغيل Container: docker-compose up -d"
    fi
else
    echo -e "      ${RED}${CROSS} Docker لا يعمل${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    add_recommendation "قم بتشغيل Docker Desktop"
    show_recommendations
    exit 1
fi
echo ""

# 2. التحقق من ODBC Driver
echo -e "${BLUE}[2/8]${NC} ${INFO} التحقق من ODBC Driver - Checking ODBC Driver..."
DRIVER_CHECK=$(docker exec hr-ml-system odbcinst -q -d 2>/dev/null)
if echo "$DRIVER_CHECK" | grep -q "ODBC Driver 17 for SQL Server"; then
    echo -e "      ${GREEN}${CHECK} ODBC Driver 17 for SQL Server مثبت${NC}"
else
    echo -e "      ${RED}${CROSS} ODBC Driver غير مثبت${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    add_recommendation "أعد بناء Container: docker-compose build --no-cache && docker-compose up -d"
fi
echo ""

# 3. طلب معلومات SQL Server
echo -e "${BLUE}[3/8]${NC} ${INFO} معلومات SQL Server - SQL Server Information..."
echo ""
echo -e "${CYAN}هل SQL Server على نفس الجهاز أم جهاز آخر؟${NC}"
echo -e "${CYAN}Is SQL Server on the same machine or a different one?${NC}"
echo ""
echo "1) نفس الجهاز (Local) - Same machine"
echo "2) جهاز آخر (Remote) - Different machine"
echo ""
read -p "اختر (1 أو 2): " SQL_LOCATION

if [ "$SQL_LOCATION" = "1" ]; then
    echo -e "      ${INFO} SQL Server محلي - Local SQL Server"
    SQL_HOST="host.docker.internal"
    IS_LOCAL=true
    echo ""
    echo -e "${YELLOW}${WARNING} ملاحظة مهمة: لا تستخدم localhost أو 127.0.0.1${NC}"
    echo -e "${YELLOW}   Important: Don't use localhost or 127.0.0.1${NC}"
    echo -e "${GREEN}   استخدم: host.docker.internal${NC}"
    echo ""
else
    echo -e "      ${INFO} SQL Server بعيد - Remote SQL Server"
    IS_LOCAL=false
    echo ""
    read -p "أدخل عنوان IP للـ SQL Server: " SQL_HOST
fi

read -p "أدخل المنفذ (افتراضي 1433): " SQL_PORT
SQL_PORT=${SQL_PORT:-1433}

read -p "أدخل اسم قاعدة البيانات: " SQL_DATABASE
read -p "أدخل اسم المستخدم: " SQL_USERNAME
read -sp "أدخل كلمة المرور: " SQL_PASSWORD
echo ""
echo ""

# 4. اختبار الاتصال من الجهاز المضيف
echo -e "${BLUE}[4/8]${NC} ${MAGNIFY} اختبار الاتصال من الجهاز المضيف - Testing from Host..."

# تحديد العنوان للاختبار من Host
if [ "$IS_LOCAL" = true ]; then
    TEST_HOST="localhost"
else
    TEST_HOST="$SQL_HOST"
fi

# اختبار المنفذ باستخدام PowerShell (Windows)
echo -e "      ${INFO} اختبار المنفذ $SQL_PORT..."
PORT_TEST=$(powershell.exe -Command "Test-NetConnection -ComputerName $TEST_HOST -Port $SQL_PORT -WarningAction SilentlyContinue | Select-Object -ExpandProperty TcpTestSucceeded" 2>/dev/null | tr -d '\r')

if [ "$PORT_TEST" = "True" ]; then
    echo -e "      ${GREEN}${CHECK} المنفذ $SQL_PORT مفتوح ويمكن الوصول إليه${NC}"
else
    echo -e "      ${RED}${CROSS} المنفذ $SQL_PORT مغلق أو غير قابل للوصول${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    
    if [ "$IS_LOCAL" = true ]; then
        add_recommendation "تأكد من أن SQL Server يعمل: افتح Services.msc وابحث عن SQL Server"
        add_recommendation "تأكد من تفعيل TCP/IP في SQL Server Configuration Manager"
        add_recommendation "أضف قاعدة Firewall للمنفذ 1433: New-NetFirewallRule -DisplayName 'SQL Server' -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow"
    else
        add_recommendation "تحقق من أن SQL Server يعمل على الجهاز البعيد"
        add_recommendation "تحقق من Firewall على الجهاز البعيد"
        add_recommendation "تحقق من أن عنوان IP صحيح: $SQL_HOST"
    fi
fi
echo ""

# 5. التحقق من SQL Server Configuration (للـ Local فقط)
if [ "$IS_LOCAL" = true ]; then
    echo -e "${BLUE}[5/8]${NC} ${WRENCH} التحقق من إعدادات SQL Server - Checking SQL Server Config..."
    
    # التحقق من خدمة SQL Server
    echo -e "      ${INFO} التحقق من خدمة SQL Server..."
    SQL_SERVICE=$(powershell.exe -Command "Get-Service -Name 'MSSQL*' | Where-Object {$_.Status -eq 'Running'} | Select-Object -First 1 -ExpandProperty Name" 2>/dev/null | tr -d '\r')
    
    if [ -n "$SQL_SERVICE" ]; then
        echo -e "      ${GREEN}${CHECK} خدمة SQL Server تعمل: $SQL_SERVICE${NC}"
    else
        echo -e "      ${RED}${CROSS} خدمة SQL Server لا تعمل${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        add_recommendation "ابدأ خدمة SQL Server من Services.msc"
    fi
    
    # التحقق من SQL Server Browser
    echo -e "      ${INFO} التحقق من SQL Server Browser..."
    BROWSER_SERVICE=$(powershell.exe -Command "Get-Service -Name 'SQLBrowser' | Select-Object -ExpandProperty Status" 2>/dev/null | tr -d '\r')
    
    if [ "$BROWSER_SERVICE" = "Running" ]; then
        echo -e "      ${GREEN}${CHECK} SQL Server Browser يعمل${NC}"
    else
        echo -e "      ${YELLOW}${WARNING} SQL Server Browser لا يعمل (مطلوب للـ Named Instances)${NC}"
        add_recommendation "إذا كنت تستخدم Named Instance (مثل SQLEXPRESS)، قم بتشغيل SQL Server Browser"
    fi
else
    echo -e "${BLUE}[5/8]${NC} ${INFO} تخطي فحص الإعدادات (SQL Server بعيد)..."
fi
echo ""

# 6. اختبار الاتصال من داخل Docker
echo -e "${BLUE}[6/8]${NC} ${MAGNIFY} اختبار الاتصال من داخل Docker - Testing from Docker..."

# إنشاء ملف Python للاختبار
cat > /tmp/test_sql_connection.py << EOF
import pyodbc
import sys

try:
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=$SQL_HOST,$SQL_PORT;"
        f"DATABASE=$SQL_DATABASE;"
        f"UID=$SQL_USERNAME;"
        f"PWD=$SQL_PASSWORD;"
        f"Timeout=10;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"SUCCESS:{version[:100]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR:{str(e)}")
    sys.exit(1)
EOF

# نسخ الملف إلى Container
docker cp /tmp/test_sql_connection.py hr-ml-system:/tmp/test_sql_connection.py 2>/dev/null

# تشغيل الاختبار
DOCKER_TEST=$(docker exec hr-ml-system python /tmp/test_sql_connection.py 2>&1)

if echo "$DOCKER_TEST" | grep -q "SUCCESS:"; then
    VERSION=$(echo "$DOCKER_TEST" | sed 's/SUCCESS://')
    echo -e "      ${GREEN}${CHECK} الاتصال ناجح من داخل Docker!${NC}"
    echo -e "      ${GREEN}${INFO} SQL Server Version: ${VERSION:0:80}...${NC}"
else
    echo -e "      ${RED}${CROSS} فشل الاتصال من داخل Docker${NC}"
    ERROR_MSG=$(echo "$DOCKER_TEST" | sed 's/ERROR://')
    echo -e "      ${RED}${INFO} الخطأ: $ERROR_MSG${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    
    # تحليل نوع الخطأ
    if echo "$ERROR_MSG" | grep -qi "timeout"; then
        add_recommendation "زد قيمة Timeout في .env: SQL_SERVER_TIMEOUT=60"
        if [ "$IS_LOCAL" = true ]; then
            add_recommendation "تأكد من استخدام host.docker.internal وليس localhost"
        fi
    elif echo "$ERROR_MSG" | grep -qi "login failed"; then
        add_recommendation "تحقق من اسم المستخدم وكلمة المرور"
        add_recommendation "تأكد من تفعيل SQL Server Authentication في SQL Server Properties → Security"
    elif echo "$ERROR_MSG" | grep -qi "cannot open database"; then
        add_recommendation "تحقق من اسم قاعدة البيانات: $SQL_DATABASE"
        add_recommendation "تأكد من أن المستخدم لديه صلاحيات على قاعدة البيانات"
    fi
fi

# تنظيف
rm -f /tmp/test_sql_connection.py
docker exec hr-ml-system rm -f /tmp/test_sql_connection.py 2>/dev/null
echo ""

# 7. اختبار API
echo -e "${BLUE}[7/8]${NC} ${MAGNIFY} اختبار API - Testing API..."

# حفظ الإعدادات مؤقتاً
docker exec hr-ml-system bash -c "
export SQL_SERVER_HOST='$SQL_HOST'
export SQL_SERVER_PORT='$SQL_PORT'
export SQL_SERVER_DATABASE='$SQL_DATABASE'
export SQL_SERVER_USERNAME='$SQL_USERNAME'
export SQL_SERVER_PASSWORD='$SQL_PASSWORD'
" 2>/dev/null

sleep 2

API_TEST=$(curl -s -X GET "http://localhost:1234/health/liveness" 2>/dev/null)
if echo "$API_TEST" | grep -q "alive"; then
    echo -e "      ${GREEN}${CHECK} API يعمل بشكل صحيح${NC}"
else
    echo -e "      ${YELLOW}${WARNING} API لا يستجيب (قد يكون النظام لا يزال يبدأ)${NC}"
fi
echo ""

# 8. إنشاء ملف .env
echo -e "${BLUE}[8/8]${NC} ${WRENCH} إنشاء ملف الإعدادات - Creating Configuration..."
echo ""

cat > .env.diagnostic << EOF
# إعدادات قاعدة البيانات - Database Settings
# تم إنشاؤها بواسطة أداة التشخيص - Generated by Diagnostic Tool

SQL_SERVER_HOST=$SQL_HOST
SQL_SERVER_PORT=$SQL_PORT
SQL_SERVER_DATABASE=$SQL_DATABASE
SQL_SERVER_USERNAME=$SQL_USERNAME
SQL_SERVER_PASSWORD=$SQL_PASSWORD
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_TIMEOUT=60
DEFAULT_EMPLOYEE_TABLE=Employees
EOF

echo -e "${GREEN}${CHECK} تم إنشاء ملف .env.diagnostic${NC}"
echo ""

# عرض الملخص
echo "========================================="
echo -e "${CYAN}${INFO} ملخص التشخيص - Diagnostic Summary${NC}"
echo "========================================="
echo ""
echo -e "${INFO} نوع SQL Server: $([ "$IS_LOCAL" = true ] && echo "محلي (Local)" || echo "بعيد (Remote)")"
echo -e "${INFO} العنوان: $SQL_HOST:$SQL_PORT"
echo -e "${INFO} قاعدة البيانات: $SQL_DATABASE"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}${CHECK}${CHECK}${CHECK} لم يتم العثور على مشاكل! ${CHECK}${CHECK}${CHECK}${NC}"
    echo -e "${GREEN}الاتصال يعمل بشكل صحيح!${NC}"
    echo ""
    echo "========================================="
    echo -e "${CYAN}${ROCKET} الخطوات التالية - Next Steps${NC}"
    echo "========================================="
    echo ""
    echo "1. انسخ الإعدادات إلى .env:"
    echo -e "   ${YELLOW}cp .env.diagnostic .env${NC}"
    echo ""
    echo "2. أعد تشغيل Container:"
    echo -e "   ${YELLOW}docker-compose restart${NC}"
    echo ""
    echo "3. افتح لوحة التحكم:"
    echo -e "   ${YELLOW}http://localhost:1234/static/dashboard/index.html${NC}"
    echo ""
else
    echo -e "${RED}${CROSS} تم العثور على $ISSUES_FOUND مشكلة/مشاكل${NC}"
    echo ""
    show_recommendations
    
    echo "========================================="
    echo -e "${CYAN}${WRENCH} خطوات الإصلاح - Fix Steps${NC}"
    echo "========================================="
    echo ""
    echo "1. قم بتطبيق التوصيات أعلاه"
    echo "2. أعد تشغيل هذا السكريبت للتحقق"
    echo "3. راجع ملف SQL_SERVER_TIMEOUT_TROUBLESHOOTING.md للمزيد من المساعدة"
    echo ""
fi

echo "========================================="
echo -e "${INFO} ملف الإعدادات المقترح: .env.diagnostic"
echo "========================================="
cat .env.diagnostic
echo ""

echo "========================================="
echo -e "${INFO} انتهى التشخيص - Diagnosis Complete"
echo "========================================="

