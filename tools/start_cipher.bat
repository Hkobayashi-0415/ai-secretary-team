@echo off
echo ================================================
echo    Cipher MCP Server - Aggregator Mode (永続版)
echo ================================================
echo.

REM 環境変数を確実に設定
set MCP_SERVER_MODE=aggregator
set AGGREGATOR_CONFLICT_RESOLUTION=prefix
set AGGREGATOR_TIMEOUT=120000

REM .envファイルからAPI KEYを読み込み
for /f "tokens=1,2 delims==" %%a in ('findstr "GEMINI_API_KEY" cipher-source\.env') do (
    set GEMINI_API_KEY=%%b
)

echo 設定:
echo - Mode: %MCP_SERVER_MODE%
echo - Conflict Resolution: %AGGREGATOR_CONFLICT_RESOLUTION%
echo - Timeout: %AGGREGATOR_TIMEOUT%ms
echo.
echo サーバーを起動中...
echo ------------------------------------------------

cd cipher-source
node dist\src\app\index.cjs --mode mcp --agent memAgent\cipher.yml

pause