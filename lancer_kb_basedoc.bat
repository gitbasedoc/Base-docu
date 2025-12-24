@echo off
REM ============================================================
REM Script de lancement KB Support Basedoc - Mode Standalone
REM ============================================================

echo.
echo ============================================================
echo   KB Support Basedoc - Lancement
echo ============================================================
echo.

REM Se placer dans le repertoire du script
cd /d "%~dp0"

REM Verifier que Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo.
    echo Telechargez Python depuis : https://www.python.org/downloads/
    echo N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

REM Verifier que l'environnement virtuel existe
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
)

REM Activer l'environnement virtuel
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Verifier que les dependances sont installees
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dependances...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer les dependances
        pause
        exit /b 1
    )
    echo [OK] Dependances installees
)

REM Verifier que la base de donnees existe
if not exist "data\kb_basedoc.db" (
    echo [INFO] Initialisation de la base de donnees...
    python standalone.py init-db
    if errorlevel 1 (
        echo [ERREUR] Impossible d'initialiser la base de donnees
        pause
        exit /b 1
    )
    echo [OK] Base de donnees initialisee
)

REM Lancer l'application
echo.
echo [INFO] Lancement de l'application...
echo.
python standalone.py

REM Si l'application s'arrete
echo.
echo [INFO] Application arretee
pause
