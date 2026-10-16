@echo off
title TRAI Telecom Analytics Dashboard
color 1F

echo.
echo  =========================================================
echo    TRAI Telecom Analytics Dashboard
echo    Author : Harshwardhan Patil
echo    College: Bharati Vidyapeeth College of Engineering
echo  =========================================================
echo.
echo  Starting dashboard... Your browser will open automatically.
echo  Press Ctrl+C in this window to stop the app.
echo.

set PY=C:\Users\intel\AppData\Local\Programs\Python\Python311\python.exe
set STREAMLIT=C:\Users\intel\AppData\Local\Programs\Python\Python311\Scripts\streamlit.exe
set APP=HarshwardhanPatil_TRAI_App.py

cd /d "%~dp0"

"%STREAMLIT%" run "%APP%" --server.port 8501 --browser.gatherUsageStats false --theme.primaryColor "#1a3a5c" --theme.backgroundColor "#f0f2f5" --theme.secondaryBackgroundColor "#ffffff" --theme.textColor "#1f2328"

pause
