@echo on
pyinstaller --onefile "fsrv_assigner.py" --name "fsrv_assigner" --noconsole --version-file file_version_info.txt --distpath="bin"
Xcopy /E .\config\ .\bin\config\
pause