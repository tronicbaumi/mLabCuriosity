@echo off
setlocal

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ============================================================
echo  mLabScope installer build
echo ============================================================

:: ---------- ensure venv exists ----------
if not exist "venv\Scripts\python.exe" (
    echo ERROR: venv not found. Run:  python -m venv venv  then install deps.
    exit /b 1
)

:: ---------- ensure PyInstaller is present ----------
venv\Scripts\pip.exe show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    venv\Scripts\pip.exe install pyinstaller
)

:: ---------- clean previous build ----------
if exist dist\mLabScope (
    echo Removing old dist\mLabScope...
    rmdir /s /q dist\mLabScope
)
if exist build\mLabScope (
    echo Removing old build\mLabScope...
    rmdir /s /q build\mLabScope
)

:: ---------- run PyInstaller ----------
echo.
echo Running PyInstaller...
venv\Scripts\pyinstaller.exe --noconfirm mlab_scope.spec
if errorlevel 1 (
    echo.
    echo BUILD FAILED — see output above.
    exit /b 1
)

echo.
echo ============================================================
echo  Build complete:  dist\mLabScope\mLabScope.exe
echo ============================================================
echo.

:: ---------- optional: open output folder ----------
explorer dist\mLabScope

endlocal
