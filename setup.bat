@echo off

title Serial-BERT (Setup)


set DIR=%~dp0

if exist %DIR%.env\ (set ENVDIR=%DIR%.env\ & goto setup_pip)
if exist %DIR%.venv\ (set ENVDIR=%DIR%.venv\ & goto setup_pip)
if exist %DIR%env\ (set ENVDIR=%DIR%env\ & goto setup_pip)
if exist %DIR%venv\ (set ENVDIR=%DIR%venv\ & goto setup_pip)


:setup_venv
echo Configuring python environment...
set ENVDIR=%DIR%.venv\
call python -m venv %DIR%.venv
goto setup_pip


:setup_pip
echo Configuring python packages...
call %ENVDIR%Scripts\activate.bat & pip install -r requirements


:exit_setup
echo Finishing setup...
echo ^@echo off > %DIR%run.bat
echo call %ENVDIR%Scripts\activate.bat ^& python main.py ^--no-show >> %DIR%run.bat
echo. && echo.
pause