"""
وحدة الاتصال بقاعدة البيانات - Database Connection Module
توفر وظائف للاتصال بـ SQL Server وتحميل البيانات
"""

import pyodbc
import pymssql
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional, Dict, Any, List
from loguru import logger
import urllib.parse

from app.config import (
    SQL_SERVER_HOST,
    SQL_SERVER_PORT,
    SQL_SERVER_DATABASE,
    SQL_SERVER_USERNAME,
    SQL_SERVER_PASSWORD,
    SQL_SERVER_DRIVER,
    SQL_SERVER_TIMEOUT,
    DEFAULT_EMPLOYEE_TABLE,
    DEFAULT_SQL_QUERY
)


class DatabaseConnection:
    """مدير الاتصال بقاعدة البيانات - Database Connection Manager"""

    def __init__(self, host=None, port=None, database=None, username=None, password=None, driver=None, timeout=None):
        """
        تهيئة مدير الاتصال - Initialize connection manager

        Parameters:
            host: عنوان الخادم (اختياري - يستخدم .env إذا لم يُحدد)
            port: المنفذ (اختياري)
            database: اسم قاعدة البيانات (اختياري)
            username: اسم المستخدم (اختياري)
            password: كلمة المرور (اختياري)
            driver: اسم Driver (اختياري)
            timeout: مهلة الاتصال (اختياري)
        """
        self.host = host or SQL_SERVER_HOST
        self.port = port or SQL_SERVER_PORT
        self.database = database or SQL_SERVER_DATABASE
        self.username = username or SQL_SERVER_USERNAME
        self.password = password or SQL_SERVER_PASSWORD
        self.driver = driver or SQL_SERVER_DRIVER
        self.timeout = timeout or SQL_SERVER_TIMEOUT
        self.connection = None
        self.engine = None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        اختبار الاتصال بقاعدة البيانات - Test database connection

        Returns:
            نتيجة الاختبار - Test result
        """
        try:
            # محاولة الاتصال باستخدام pyodbc
            conn = self.get_pyodbc_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            logger.info(f"✅ الاتصال بقاعدة البيانات ناجح - SQL Server Version: {version[:50]}...")

            return {
                "success": True,
                "message": "الاتصال بقاعدة البيانات ناجح - Connection successful",
                "server": self.host,
                "database": self.database,
                "version": version[:100]
            }

        except Exception as e:
            logger.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")

            # محاولة باستخدام pymssql كبديل
            try:
                conn = self.get_pymssql_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                cursor.close()
                conn.close()

                logger.info(f"✅ الاتصال بقاعدة البيانات ناجح (pymssql) - SQL Server Version: {version[:50]}...")

                return {
                    "success": True,
                    "message": "الاتصال بقاعدة البيانات ناجح (pymssql) - Connection successful",
                    "server": self.host,
                    "database": self.database,
                    "version": version[:100],
                    "driver": "pymssql"
                }

            except Exception as e2:
                logger.error(f"❌ فشل الاتصال بقاعدة البيانات (pymssql): {e2}")

                # إضافة معلومات تشخيصية
                diagnostic_info = self._get_diagnostic_info(str(e), str(e2))

                return {
                    "success": False,
                    "message": f"فشل الاتصال بقاعدة البيانات - Connection failed: {str(e)}",
                    "error": str(e),
                    "alternative_error": str(e2),
                    "diagnostic": diagnostic_info
                }

    def _get_diagnostic_info(self, error1: str, error2: str) -> Dict[str, Any]:
        """
        الحصول على معلومات تشخيصية - Get diagnostic information

        Args:
            error1: الخطأ الأول - First error
            error2: الخطأ الثاني - Second error

        Returns:
            معلومات تشخيصية - Diagnostic information
        """
        diagnostic = {
            "error_type": "unknown",
            "possible_causes": [],
            "solutions": []
        }

        error_combined = (error1 + " " + error2).lower()

        # تحليل نوع الخطأ
        if "timeout" in error_combined or "hyt00" in error_combined:
            diagnostic["error_type"] = "timeout"
            diagnostic["possible_causes"] = [
                "عنوان Server خاطئ - Incorrect server address",
                "SQL Server لا يقبل اتصالات TCP/IP - SQL Server not accepting TCP/IP",
                "Firewall يحجب المنفذ 1433 - Firewall blocking port 1433",
                "استخدام localhost بدلاً من host.docker.internal - Using localhost instead of host.docker.internal"
            ]
            diagnostic["solutions"] = [
                "إذا كان SQL Server محلي، استخدم: host.docker.internal - If local, use: host.docker.internal",
                "تأكد من تفعيل TCP/IP في SQL Server Configuration Manager",
                "أضف قاعدة Firewall: New-NetFirewallRule -DisplayName 'SQL Server' -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow",
                "زد قيمة Timeout في .env: SQL_SERVER_TIMEOUT=60"
            ]

        elif "login failed" in error_combined or "28000" in error_combined:
            diagnostic["error_type"] = "authentication"
            diagnostic["possible_causes"] = [
                "اسم المستخدم أو كلمة المرور خاطئة - Wrong username or password",
                "SQL Server Authentication غير مفعّل - SQL Server Authentication not enabled",
                "المستخدم ليس لديه صلاحيات - User doesn't have permissions"
            ]
            diagnostic["solutions"] = [
                "تحقق من اسم المستخدم وكلمة المرور - Verify username and password",
                "فعّل SQL Server Authentication في Server Properties → Security",
                "تأكد من أن المستخدم لديه صلاحيات على قاعدة البيانات"
            ]

        elif "cannot open database" in error_combined or "42000" in error_combined:
            diagnostic["error_type"] = "database_not_found"
            diagnostic["possible_causes"] = [
                "اسم قاعدة البيانات خاطئ - Wrong database name",
                "قاعدة البيانات غير موجودة - Database doesn't exist",
                "المستخدم ليس لديه صلاحيات - User doesn't have access"
            ]
            diagnostic["solutions"] = [
                f"تحقق من اسم قاعدة البيانات: {self.database}",
                "تأكد من وجود قاعدة البيانات في SQL Server",
                "امنح المستخدم صلاحيات على قاعدة البيانات"
            ]

        elif "network" in error_combined or "08001" in error_combined:
            diagnostic["error_type"] = "network"
            diagnostic["possible_causes"] = [
                "SQL Server لا يعمل - SQL Server not running",
                "عنوان Server خاطئ - Wrong server address",
                "مشاكل في الشبكة - Network issues"
            ]
            diagnostic["solutions"] = [
                "تأكد من أن SQL Server يعمل: Services.msc",
                "تحقق من عنوان Server: " + self.host,
                "اختبر الاتصال: Test-NetConnection -ComputerName " + self.host + " -Port " + str(self.port)
            ]

        return diagnostic

    def diagnose_connection(self) -> Dict[str, Any]:
        """
        تشخيص شامل لمشكلة الاتصال - Comprehensive connection diagnosis

        Returns:
            تقرير تشخيصي - Diagnostic report
        """
        logger.info("🔍 بدء التشخيص الشامل - Starting comprehensive diagnosis")

        diagnosis = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "configuration": {
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "username": self.username,
                "driver": self.driver,
                "timeout": self.timeout
            },
            "checks": {},
            "recommendations": [],
            "overall_status": "unknown"
        }

        # 1. فحص ODBC Drivers المتاحة
        available_drivers = self.get_available_drivers()
        diagnosis["checks"]["odbc_drivers"] = {
            "available": available_drivers,
            "status": "ok" if available_drivers else "error",
            "message": f"تم العثور على {len(available_drivers)} driver(s)" if available_drivers else "لم يتم العثور على drivers"
        }

        if not available_drivers:
            diagnosis["recommendations"].append({
                "priority": "high",
                "message": "قم بإعادة بناء Docker container لتثبيت ODBC Driver",
                "command": "docker-compose build --no-cache && docker-compose up -d"
            })

        # 2. فحص إعدادات الاتصال
        config_issues = []

        if self.host in ["localhost", "127.0.0.1", "(local)"]:
            config_issues.append("استخدام localhost - يجب استخدام host.docker.internal للـ SQL Server المحلي")
            diagnosis["recommendations"].append({
                "priority": "critical",
                "message": "استخدم host.docker.internal بدلاً من localhost",
                "fix": "SQL_SERVER_HOST=host.docker.internal"
            })

        if not self.password:
            config_issues.append("كلمة المرور فارغة")
            diagnosis["recommendations"].append({
                "priority": "high",
                "message": "تأكد من إدخال كلمة المرور في .env",
                "fix": "SQL_SERVER_PASSWORD=YourPassword"
            })

        diagnosis["checks"]["configuration"] = {
            "status": "ok" if not config_issues else "warning",
            "issues": config_issues
        }

        # 3. محاولة الاتصال وتحليل الخطأ
        try:
            conn = self.get_pyodbc_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION, DB_NAME(), SUSER_NAME()")
            result = cursor.fetchone()
            version = result[0]
            current_db = result[1]
            current_user = result[2]
            cursor.close()
            conn.close()

            diagnosis["checks"]["connection"] = {
                "status": "success",
                "message": "الاتصال ناجح",
                "details": {
                    "version": version[:100],
                    "current_database": current_db,
                    "current_user": current_user
                }
            }
            diagnosis["overall_status"] = "success"

        except Exception as e:
            error_str = str(e)
            diagnosis["checks"]["connection"] = {
                "status": "error",
                "message": "فشل الاتصال",
                "error": error_str
            }

            # تحليل تفصيلي للخطأ
            diagnostic_info = self._get_diagnostic_info(error_str, "")
            diagnosis["error_analysis"] = diagnostic_info

            # إضافة التوصيات من التحليل
            for solution in diagnostic_info.get("solutions", []):
                diagnosis["recommendations"].append({
                    "priority": "high",
                    "message": solution
                })

            diagnosis["overall_status"] = "error"

        # 4. فحص الشبكة (إذا فشل الاتصال)
        if diagnosis["overall_status"] == "error":
            diagnosis["checks"]["network"] = {
                "status": "info",
                "message": f"تحقق من إمكانية الوصول إلى {self.host}:{self.port}",
                "test_command": f"Test-NetConnection -ComputerName {self.host} -Port {self.port}"
            }

        logger.info(f"✅ انتهى التشخيص - Status: {diagnosis['overall_status']}")
        return diagnosis
    
    def get_available_drivers(self) -> List[str]:
        """
        الحصول على قائمة drivers المتاحة - Get list of available drivers

        Returns:
            قائمة drivers - List of available drivers
        """
        try:
            drivers = pyodbc.drivers()
            logger.info(f"ODBC Drivers المتاحة: {drivers}")
            return drivers
        except Exception as e:
            logger.warning(f"فشل الحصول على قائمة drivers: {e}")
            return []

    def get_best_driver(self) -> str:
        """
        الحصول على أفضل driver متاح - Get best available driver

        Returns:
            اسم driver - Driver name
        """
        available_drivers = self.get_available_drivers()

        # قائمة drivers بالترتيب من الأفضل إلى الأقل
        preferred_drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 13 for SQL Server",
            "ODBC Driver 11 for SQL Server",
            "FreeTDS",
            "SQL Server"
        ]

        for driver in preferred_drivers:
            if driver in available_drivers:
                logger.info(f"تم اختيار driver: {driver}")
                return driver

        # إذا لم يتم العثور على أي driver، استخدام الافتراضي
        if available_drivers:
            logger.warning(f"استخدام driver افتراضي: {available_drivers[0]}")
            return available_drivers[0]

        # إذا لم يتم العثور على أي driver، استخدام القيمة من config
        logger.warning(f"لم يتم العثور على drivers، استخدام: {self.driver}")
        return self.driver

    def get_pyodbc_connection(self):
        """
        الحصول على اتصال pyodbc - Get pyodbc connection

        Returns:
            اتصال قاعدة البيانات - Database connection
        """
        # محاولة استخدام driver محدد أولاً
        driver = self.driver

        try:
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"Timeout={self.timeout};"
            )

            logger.info(f"الاتصال بـ SQL Server باستخدام {driver}: {self.host}:{self.port}/{self.database}")
            return pyodbc.connect(connection_string)

        except Exception as e:
            logger.warning(f"فشل الاتصال باستخدام {driver}: {e}")

            # محاولة استخدام أفضل driver متاح
            best_driver = self.get_best_driver()

            if best_driver != driver:
                try:
                    connection_string = (
                        f"DRIVER={{{best_driver}}};"
                        f"SERVER={self.host},{self.port};"
                        f"DATABASE={self.database};"
                        f"UID={self.username};"
                        f"PWD={self.password};"
                        f"Timeout={self.timeout};"
                    )

                    logger.info(f"محاولة الاتصال باستخدام {best_driver}")
                    return pyodbc.connect(connection_string)

                except Exception as e2:
                    logger.error(f"فشل الاتصال باستخدام {best_driver}: {e2}")
                    raise
            else:
                raise
    
    def get_pymssql_connection(self):
        """
        الحصول على اتصال pymssql - Get pymssql connection
        
        Returns:
            اتصال قاعدة البيانات - Database connection
        """
        logger.info(f"الاتصال بـ SQL Server (pymssql): {self.host}:{self.port}/{self.database}")
        return pymssql.connect(
            server=self.host,
            port=int(self.port),
            user=self.username,
            password=self.password,
            database=self.database,
            timeout=self.timeout
        )
    
    def get_sqlalchemy_engine(self):
        """
        الحصول على محرك SQLAlchemy - Get SQLAlchemy engine
        
        Returns:
            محرك قاعدة البيانات - Database engine
        """
        if self.engine is None:
            # محاولة استخدام pyodbc أولاً
            try:
                params = urllib.parse.quote_plus(
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.host},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )
                connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
                self.engine = create_engine(connection_string, echo=False)
                logger.info("تم إنشاء محرك SQLAlchemy (pyodbc)")
            
            except Exception as e:
                logger.warning(f"فشل إنشاء محرك pyodbc: {e}")
                
                # محاولة استخدام pymssql كبديل
                try:
                    connection_string = (
                        f"mssql+pymssql://{self.username}:{self.password}@"
                        f"{self.host}:{self.port}/{self.database}"
                    )
                    self.engine = create_engine(connection_string, echo=False)
                    logger.info("تم إنشاء محرك SQLAlchemy (pymssql)")
                
                except Exception as e2:
                    logger.error(f"فشل إنشاء محرك SQLAlchemy: {e2}")
                    raise
        
        return self.engine
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        تنفيذ استعلام SQL وإرجاع النتائج - Execute SQL query and return results
        
        Args:
            query: استعلام SQL - SQL query
        
        Returns:
            نتائج الاستعلام - Query results as DataFrame
        """
        try:
            # محاولة استخدام SQLAlchemy
            engine = self.get_sqlalchemy_engine()
            df = pd.read_sql(query, engine)
            logger.info(f"تم تنفيذ الاستعلام بنجاح: {len(df)} صف")
            return df
        
        except Exception as e:
            logger.error(f"فشل تنفيذ الاستعلام باستخدام SQLAlchemy: {e}")
            
            # محاولة استخدام pyodbc مباشرة
            try:
                conn = self.get_pyodbc_connection()
                df = pd.read_sql(query, conn)
                conn.close()
                logger.info(f"تم تنفيذ الاستعلام بنجاح (pyodbc): {len(df)} صف")
                return df
            
            except Exception as e2:
                logger.error(f"فشل تنفيذ الاستعلام باستخدام pyodbc: {e2}")
                
                # محاولة استخدام pymssql كبديل أخير
                try:
                    conn = self.get_pymssql_connection()
                    df = pd.read_sql(query, conn)
                    conn.close()
                    logger.info(f"تم تنفيذ الاستعلام بنجاح (pymssql): {len(df)} صف")
                    return df
                
                except Exception as e3:
                    logger.error(f"فشل تنفيذ الاستعلام: {e3}")
                    raise Exception(f"فشل تنفيذ الاستعلام بجميع الطرق: {str(e)}, {str(e2)}, {str(e3)}")
    
    def load_employee_data(
        self,
        table_name: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        تحميل بيانات الموظفين من قاعدة البيانات - Load employee data from database
        
        Args:
            table_name: اسم الجدول - Table name (optional)
            query: استعلام SQL مخصص - Custom SQL query (optional)
            limit: حد عدد الصفوف - Row limit (optional)
        
        Returns:
            بيانات الموظفين - Employee data as DataFrame
        """
        if query:
            # استخدام الاستعلام المخصص
            final_query = query
        elif table_name:
            # استخدام اسم الجدول
            final_query = f"SELECT * FROM {table_name}"
        else:
            # استخدام الجدول الافتراضي
            final_query = DEFAULT_SQL_QUERY
        
        # إضافة حد للصفوف إذا تم تحديده
        if limit:
            final_query = f"SELECT TOP {limit} * FROM ({final_query}) AS subquery"
        
        logger.info(f"تحميل بيانات الموظفين: {final_query[:100]}...")
        
        df = self.execute_query(final_query)
        
        logger.info(f"تم تحميل {len(df)} موظف، {len(df.columns)} عمود")
        
        return df
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        الحصول على معلومات الجدول - Get table information
        
        Args:
            table_name: اسم الجدول - Table name
        
        Returns:
            معلومات الجدول - Table information
        """
        try:
            # الحصول على عدد الصفوف
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_df = self.execute_query(count_query)
            row_count = count_df['count'].iloc[0]
            
            # الحصول على أسماء الأعمدة
            columns_query = f"SELECT TOP 1 * FROM {table_name}"
            sample_df = self.execute_query(columns_query)
            columns = list(sample_df.columns)
            
            return {
                "table_name": table_name,
                "row_count": int(row_count),
                "column_count": len(columns),
                "columns": columns
            }
        
        except Exception as e:
            logger.error(f"فشل الحصول على معلومات الجدول: {e}")
            raise
    
    def list_tables(self) -> List[str]:
        """
        الحصول على قائمة الجداول - Get list of tables
        
        Returns:
            قائمة أسماء الجداول - List of table names
        """
        try:
            query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
            df = self.execute_query(query)
            tables = df['TABLE_NAME'].tolist()
            logger.info(f"تم العثور على {len(tables)} جدول")
            return tables
        
        except Exception as e:
            logger.error(f"فشل الحصول على قائمة الجداول: {e}")
            raise
    
    def close(self):
        """إغلاق الاتصال - Close connection"""
        if self.connection:
            self.connection.close()
            logger.info("تم إغلاق الاتصال بقاعدة البيانات")
        
        if self.engine:
            self.engine.dispose()
            logger.info("تم إغلاق محرك SQLAlchemy")


# إنشاء نسخة عامة - Create global instance
db = DatabaseConnection()

