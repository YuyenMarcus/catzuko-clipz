@echo off
echo ========================================
echo Pushing to GitHub
echo ========================================
echo.

git add .
git commit -m "Update Clipfarm Dashboard"
git push origin main

echo.
echo ========================================
echo Pushed to GitHub!
echo ========================================
echo.
echo Vercel will automatically deploy if connected.
echo.
pause

