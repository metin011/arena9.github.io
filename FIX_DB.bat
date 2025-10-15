@echo off
echo Uygulamayi kapatiyorum...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Eski veritabanini siliyorum...
del football_stats.db 2>nul

echo Yeni veritabani olusturuluyor...
python reset_db.py

echo.
echo HAZIR! Simdi uygulamayi baslat:
echo python app_updated.py
pause
