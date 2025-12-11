@echo off
echo Starting LLM Research Summarizer Web UI...
echo.
echo The UI will open in your browser at: http://127.0.0.1:7860
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
.venv\Scripts\python.exe app_ui.py

pause
