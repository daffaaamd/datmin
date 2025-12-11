@echo off
REM Streamlit Dashboard Wisata Indonesia
REM Script untuk menjalankan aplikasi

echo Memulai Dashboard Wisata Indonesia...
echo.

REM Gunakan python dari PATH atau full path jika perlu
python -m streamlit run app.py --logger.level=error

REM Jika command di atas tidak bekerja, coba dengan py (Windows Python Launcher)
REM py -m streamlit run app.py --logger.level=error

pause
