@echo off
REM Cog Helper Script for HR-ML System (Windows)
REM سكريبت مساعد Cog لنظام الموارد البشرية

setlocal enabledelayedexpansion

REM Check if command is provided
if "%1"=="" (
    call :show_usage
    exit /b 1
)

REM Process commands
if /i "%1"=="check" (
    call :check_all
) else if /i "%1"=="build" (
    call :build_cog
) else if /i "%1"=="test" (
    call :test_predict
) else if /i "%1"=="run" (
    call :run_server %2
) else if /i "%1"=="push" (
    call :push_replicate %2
) else if /i "%1"=="help" (
    call :show_usage
) else (
    echo [ERROR] Unknown command: %1
    call :show_usage
    exit /b 1
)

exit /b 0

:check_model
    if exist "models\promotion_model.joblib" (
        echo [OK] Model found: models\promotion_model.joblib
        exit /b 0
    ) else (
        echo [ERROR] Model not found: models\promotion_model.joblib
        echo [WARNING] Please train the model first using FastAPI or Python script
        exit /b 1
    )

:check_cog
    where cog >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Cog is installed
        cog --version
        exit /b 0
    ) else (
        echo [ERROR] Cog is not installed
        echo [INFO] Install Cog from: https://github.com/replicate/cog
        exit /b 1
    )

:check_all
    echo [INFO] Checking prerequisites...
    call :check_cog
    if %errorlevel% neq 0 exit /b 1
    call :check_model
    if %errorlevel% neq 0 exit /b 1
    echo [OK] All checks passed!
    exit /b 0

:build_cog
    echo [INFO] Building Cog image...
    
    call :check_model
    if %errorlevel% neq 0 exit /b 1
    
    call :check_cog
    if %errorlevel% neq 0 exit /b 1
    
    echo [INFO] Starting Cog build (this may take a few minutes)...
    cog build -t hr-ml-model
    
    if %errorlevel% equ 0 (
        echo [OK] Cog image built successfully!
        echo [INFO] Image name: hr-ml-model
    ) else (
        echo [ERROR] Cog build failed
        exit /b 1
    )
    exit /b 0

:test_predict
    echo [INFO] Testing prediction...
    
    call :check_cog
    if %errorlevel% neq 0 exit /b 1
    
    echo [INFO] Running test prediction with sample data...
    cog predict ^
        -i experience=5.0 ^
        -i education_level=7 ^
        -i performance_score=85.0 ^
        -i training_hours=40.0 ^
        -i awards=2 ^
        -i avg_work_hours=8.5 ^
        -i department="it" ^
        -i gender="male" ^
        -i language="ar"
    
    if %errorlevel% equ 0 (
        echo [OK] Test prediction completed!
    ) else (
        echo [ERROR] Test prediction failed
        exit /b 1
    )
    exit /b 0

:run_server
    echo [INFO] Starting Cog HTTP server...
    
    call :check_cog
    if %errorlevel% neq 0 exit /b 1
    
    set PORT=%1
    if "%PORT%"=="" set PORT=5000
    
    echo [INFO] Server will be available at:
    echo [INFO]   - API: http://localhost:%PORT%
    echo [INFO]   - Docs: http://localhost:%PORT%/docs
    echo [INFO]   - OpenAPI: http://localhost:%PORT%/openapi.json
    echo.
    echo [INFO] Press Ctrl+C to stop the server
    echo.
    
    cog run -p %PORT%
    exit /b 0

:push_replicate
    echo [INFO] Pushing to Replicate...
    
    call :check_cog
    if %errorlevel% neq 0 exit /b 1
    
    if "%1"=="" (
        echo [ERROR] Please provide your Replicate username
        echo [INFO] Usage: cog_helper.bat push ^<username^>
        exit /b 1
    )
    
    set USERNAME=%1
    
    echo [INFO] Logging in to Replicate...
    cog login
    
    echo [INFO] Pushing model to r8.im/%USERNAME%/hr-ml-model...
    cog push r8.im/%USERNAME%/hr-ml-model
    
    if %errorlevel% equ 0 (
        echo [OK] Model pushed successfully!
        echo [INFO] Your model is available at: https://replicate.com/%USERNAME%/hr-ml-model
    ) else (
        echo [ERROR] Push failed
        exit /b 1
    )
    exit /b 0

:show_usage
    echo.
    echo HR-ML Cog Helper Script (Windows)
    echo نظام الموارد البشرية الذكي - سكريبت مساعد Cog
    echo.
    echo Usage: cog_helper.bat ^<command^> [options]
    echo.
    echo Commands:
    echo   check       - Check if model and Cog are ready
    echo   build       - Build Cog Docker image
    echo   test        - Test prediction with sample data
    echo   run [port]  - Run Cog HTTP server (default port: 5000)
    echo   push ^<user^> - Push model to Replicate
    echo   help        - Show this help message
    echo.
    echo Examples:
    echo   cog_helper.bat check
    echo   cog_helper.bat build
    echo   cog_helper.bat test
    echo   cog_helper.bat run 5000
    echo   cog_helper.bat push your-username
    echo.
    exit /b 0

