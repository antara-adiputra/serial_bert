@echo off

title Serial-BERT (Setup)

set DIR=%~dp0
echo Directory Path = '%DIR%'

if exist %DIR%.env\ (
  set ENVDIR=%DIR%.env\
  goto setup_pip
)
if exist %DIR%.venv\ (
  set ENVDIR=%DIR%.venv\
  goto setup_pip
)
if exist %DIR%env\ (
  set ENVDIR=%DIR%env\
  goto setup_pip
)
if exist %DIR%venv\ (
  set ENVDIR=%DIR%venv\
  goto setup_pip
)


:setup_venv
echo Python virtual environment not exist, create a new one...
set ENVDIR=%DIR%.venv\
call python -m venv %DIR%.venv
goto setup_pip


:setup_pip
echo Installing required packages...
call %ENVDIR%Scripts\activate.bat
call python -m pip install -U pip setuptools & pip install -r requirements
echo.
echo Packages installed successfully!


:exit_setup
echo Finishing setup...
(
  echo ^@echo off
  echo title Serial-BERT ^(Runtime^)
  echo call %ENVDIR%Scripts\activate.bat ^& python main.py ^--no-show
) > %DIR%run.bat
echo.
pause
