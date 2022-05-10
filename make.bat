@echo on
set PY_FILE=fsrv_assigner.py
set PROJECT_NAME=fsrv_assigner
set VERSION=1.3

pyinstaller --onefile %PY_FILE% --name %PROJECT_NAME%_%VERSION% --noconsole --version-file file_version_info.txt

Rem This command below is just specific for this script

Xcopy /E ".\config\" ".\dist\config\"

Rem end of extra command

cd dist
tar -acf %PROJECT_NAME%_%VERSION%_release.zip *
pause