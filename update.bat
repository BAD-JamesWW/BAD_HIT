@echo off
echo Installing/updating required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo All dependencies are installed.
pause
