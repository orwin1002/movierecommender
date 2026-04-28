@echo off
taskkill /F /IM python.exe /T 2>nul
ping -n 3 127.0.0.1 > nul
start "Streamlit" /B python -m streamlit run app.py --server.port 8501 --server.headless true
ping -n 7 127.0.0.1 > nul
echo Deploy complete
exit 0