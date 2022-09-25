@echo OFF

CALL SetEnvs.bat
SET "NAO_HOST=127.0.0.1"
: venv\Scripts\python.exe Main.py %NAO_HOST% %NAO_PORT%
python Main.py %NAO_HOST% %NAO_PORT%