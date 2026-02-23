@echo off
:: Installation automatique de Prince XML

echo.
echo Installation de Prince XML...
echo.

python "%~dp0install_prince.py"

if errorlevel 1 (
    echo.
    echo [ERREUR] L'installation a echoue
    pause
    exit /b 1
)

echo.
echo Installation terminee !
pause
