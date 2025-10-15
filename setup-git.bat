@echo off
echo Git Kullanici Bilgilerini Ayarlama
echo ====================================
echo.

set /p username="GitHub kullanici adinizi girin: "
set /p email="Email adresinizi girin: "

git config --global user.name "%username%"
git config --global user.email "%email%"

echo.
echo ✅ Git ayarlari tamamlandi!
echo.
echo Simdi GitHub'a yukleme yapabilirsiniz:
echo 1. git add .
echo 2. git commit -m "Initial commit"
echo 3. git branch -M main
echo 4. git remote add origin https://github.com/KULLANICI_ADINIZ/football-stats-app.git
echo 5. git push -u origin main
echo.
pause
