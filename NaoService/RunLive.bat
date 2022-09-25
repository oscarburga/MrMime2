@echo OFF

CALL SetEnvs.bat
SET "NAO_HOST=192.168.1.15"
venv\Scripts\python.exe Main.py %NAO_HOST% %NAO_PORT%