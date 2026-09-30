$VENV=".venv"

& ".\$VENV\Scripts\activate"
pyinstaller --name PyKeyboard --noconsole --onefile "src\Keyboard.py"
Copy-Item -Path ".\$VENV\Scripts\AutoHotkey.exe" -Destination ".\dist" -Force
cd .\dist
.\PyKeyboard.exe # lanscape (default) or portrait mode with -p, --portrait option
$EXIT_CODE=$?
if ($EXIT_CODE) {
    echo "*** Test passed. ***"
} else {
    echo "*** Test failed! ***"
}
deactivate
exit $EXIT_CODE