$VENV=".venv"

& ".\$ENV\Scripts\activate"
pyinstaller --name PyKeyboard --noconsole --onefile src\Keyboard.py
Copy-Item -Path ".\$VENV\Scripts\AutoHotkey.exe" -Destination ".\dist" -Force
.\dist\PyKeyboard.exe # lanscape (default) or portrait mode with -p, --portrait option
deactivate
