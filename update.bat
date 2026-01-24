@echo off
echo Installing/updating required packages...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
echo.
echo All dependencies are installed.
pause
