@echo off
echo ========================================
echo Setting up Git for Vercel Deployment
echo ========================================
echo.

echo Initializing git repository...
git init

echo.
echo Adding all files...
git add .

echo.
echo Creating initial commit...
git commit -m "Initial commit - Clipfarm Dashboard with Vercel support"

echo.
echo Setting up remote repository...
git remote add origin https://github.com/YuyenMarcus/catzuko-clipz.git

echo.
echo ========================================
echo Git setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Push to GitHub: git push -u origin main
echo 2. Go to https://vercel.com
echo 3. Import project from GitHub
echo 4. Deploy!
echo.
pause

