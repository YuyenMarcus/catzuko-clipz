@echo off
echo ========================================
echo Clipfarm - Content Generation Only
echo ========================================
echo.
echo Generating clips (no auto-posting)...
echo.

python automation_system.py --no-auto-post --run-once

pause

