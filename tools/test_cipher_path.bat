@echo off
echo ================================================
echo    Cipher MCP Path Test
echo ================================================
echo.
echo Current Directory: %cd%
echo.

REM Check if Cipher exists in new location
if exist "cipher-mcp\dist\src\app\index.cjs" (
    echo [OK] Found Cipher at: cipher-mcp\dist\src\app\index.cjs
    echo.
    echo Testing Cipher version...
    node cipher-mcp\dist\src\app\index.cjs --version
) else (
    echo [ERROR] Cipher not found at expected location
    echo Expected: cipher-mcp\dist\src\app\index.cjs
)

echo.
echo Checking memAgent config...
if exist "cipher-mcp\memAgent\cipher.yml" (
    echo [OK] Found config at: cipher-mcp\memAgent\cipher.yml
) else (
    echo [ERROR] Config not found at expected location
)

echo.
echo Checking database...
if exist "..\data\cipher.db" (
    echo [OK] Found database at: ..\data\cipher.db
) else if exist "cipher-mcp\data\cipher.db" (
    echo [OK] Found database at: cipher-mcp\data\cipher.db
) else (
    echo [WARNING] Database not found
)

echo.
pause