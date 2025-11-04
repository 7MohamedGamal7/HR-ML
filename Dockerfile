# نظام الموارد البشرية الذكي - Smart HR System
# Dockerfile for containerization

# استخدام Python 3.11 كصورة أساسية - Use Python 3.11 as base image
FROM python:3.11-slim

# تعيين متغيرات البيئة - Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ACCEPT_EULA=Y

# تثبيت المكتبات المطلوبة لـ SQL Server - Install SQL Server dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Microsoft ODBC Driver 17 for SQL Server
# Install Microsoft ODBC Driver 17 for SQL Server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && ACCEPT_EULA=Y apt-get install -y mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> /etc/bash.bashrc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير جذري - Create non-root user
RUN useradd -m -u 1000 hruser && \
    mkdir -p /app && \
    chown -R hruser:hruser /app

# تعيين مجلد العمل - Set working directory
WORKDIR /app

# نسخ ملف المتطلبات - Copy requirements file
COPY --chown=hruser:hruser requirements.txt .

# تثبيت المتطلبات - Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق - Copy application files
COPY --chown=hruser:hruser . .

# إنشاء المجلدات المطلوبة - Create required directories
RUN mkdir -p data models logs policies employees && \
    chown -R hruser:hruser data models logs policies employees

# التبديل إلى المستخدم غير الجذري - Switch to non-root user
USER hruser

# كشف المنفذ - Expose port
EXPOSE 8000

# فحص الصحة - Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/liveness')"

# تشغيل التطبيق - Run application
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]

