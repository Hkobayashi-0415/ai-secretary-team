@echo off
echo Testing Cipher MCP...

REM Test if cipher works
echo.
echo Testing basic cipher command...
node cipher-source\dist\src\app\index.cjs --version

REM Test MCP mode (Aggregator Mode)
echo.
echo Testing MCP mode with Aggregator...
set GEMINI_API_KEY=%GEMINI_API_KEY%
set MCP_SERVER_MODE=aggregator
set AGGREGATOR_CONFLICT_RESOLUTION=prefix
set AGGREGATOR_TIMEOUT=120000
node cipher-source\dist\src\app\index.cjs --mode mcp --agent cipher-source\memAgent\cipher.yml

echo.
echo Test complete. If you see the MCP server output above, cipher is working correctly.
pause