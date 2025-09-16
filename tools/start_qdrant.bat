@echo off
echo ================================================
echo    Starting Qdrant Vector Database
echo ================================================
echo.

cd cipher-mcp\qdrant
echo Starting Qdrant server...
echo Press Ctrl+C to stop
echo.

qdrant.exe

pause