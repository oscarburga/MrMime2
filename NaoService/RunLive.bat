@echo OFF

CALL SetEnvs.bat
: 192.168.1.15
SET "NAO_HOST=192.168.1.15"
venv\Scripts\python.exe Main.py %NAO_HOST% %NAO_PORT%