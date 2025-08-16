@echo off
echo ================================================
echo    Cipher MCP Server - Aggregator Mode
echo ================================================
echo.
echo Starting Cipher in Aggregator Mode...
echo This will aggregate multiple MCP servers into one.
echo.

REM Set environment variables for Aggregator Mode
set MCP_SERVER_MODE=aggregator
set AGGREGATOR_CONFLICT_RESOLUTION=prefix
set AGGREGATOR_TIMEOUT=120000

REM Set API keys (update these with your actual keys)
set GEMINI_API_KEY=%GEMINI_API_KEY%

REM Optional: Set other API keys if needed
REM set OPENAI_API_KEY=your_openai_api_key_here
REM set ANTHROPIC_API_KEY=your_anthropic_api_key_here

echo Configuration:
echo - Mode: Aggregator
echo - Conflict Resolution: prefix
echo - Timeout: 120 seconds
echo - Config File: cipher-source\memAgent\cipher.yml
echo.
echo Starting server...
echo ------------------------------------------------

REM Start Cipher in MCP mode with aggregator
node cipher-source\dist\src\app\index.cjs --mode mcp --agent cipher-source\memAgent\cipher.yml

echo.
echo ------------------------------------------------
echo Server stopped.
pause