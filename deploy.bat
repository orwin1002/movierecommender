@echo off
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak > nul
start "Streamlit" /B python -m streamlit run app.py --server.port 8501 --server.headless true
timeout /t 6 /nobreak > nul
echo Deploy complete