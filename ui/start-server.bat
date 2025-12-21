@echo off
echo Starting The Twilight Zone Episode Viewer...
echo.
echo Trying to start local server...
echo.

REM Try custom Python server first (best MIME type support)
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    if exist server.py (
        echo Starting custom Python server on http://localhost:8000
        echo Press Ctrl+C to stop the server
        echo.
        python server.py
        exit /b
    )
)

REM Try Node.js
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starting server with Node.js on http://localhost:8000
    echo Press Ctrl+C to stop the server
    echo.
    start http://localhost:8000
    npx http-server -p 8000
    exit /b
)

REM Try PHP
where php >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starting server with PHP on http://localhost:8000
    echo Press Ctrl+C to stop the server
    echo.
    start http://localhost:8000
    php -S localhost:8000
    exit /b
)

echo ERROR: No suitable server found!
echo Please install Python, Node.js, or PHP to run a local server.
echo.
pause
