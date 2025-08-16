@echo off
echo ================================================
echo    Cipher MCP Server for Cursor
echo    Aggregator Mode with 21 Tools
echo ================================================
echo.

REM 環境変数を明示的に設定
set MCP_SERVER_MODE=aggregator
set AGGREGATOR_CONFLICT_RESOLUTION=prefix
set AGGREGATOR_TIMEOUT=120000

REM .envファイルからAPI KEYを読み込み
for /f "tokens=1,2 delims==" %%a in ('findstr "GEMINI_API_KEY" cipher-source\.env') do (
    set GEMINI_API_KEY=%%b
)

echo Configuration:
echo - Mode: AGGREGATOR (21 tools)
echo - MCP_SERVER_MODE: %MCP_SERVER_MODE%
echo - Conflict Resolution: %AGGREGATOR_CONFLICT_RESOLUTION%
echo - Timeout: %AGGREGATOR_TIMEOUT%ms
echo.

REM Cursorから呼び出される場合のパス対応
if exist "cipher-source\dist\src\app\index.cjs" (
    cd cipher-source
    node dist\src\app\index.cjs --mode mcp --agent memAgent\cipher.yml
) else if exist ".\dist\src\app\index.cjs" (
    node dist\src\app\index.cjs --mode mcp --agent memAgent\cipher.yml
) else (
    echo Error: Cannot find Cipher executable
    pause
    exit /b 1
)