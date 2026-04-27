@echo off
echo ========================================
echo   MongoDB Service Checker
echo ========================================
echo.

echo Checking for MongoDB services...
echo.

sc query | findstr /i "mongo"

echo.
echo ========================================
echo.
echo If you see a MongoDB service above:
echo   1. Note the service name
echo   2. Open PowerShell as Administrator
echo   3. Run: net start [service-name]
echo.
echo If no service found:
echo   MongoDB might need manual start
echo   See START_MONGODB.md for details
echo.
pause
