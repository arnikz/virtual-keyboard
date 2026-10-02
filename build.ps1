$VENV=".venv"
$NAME="Keyboard"
$OUTDIR="dist"

& ".\$VENV\Scripts\activate"
pyinstaller --name "$NAME" --noconsole --onefile "src\Keyboard.py"
Copy-Item -Path ".\$VENV\Scripts\AutoHotkey.exe" -Destination "$OUTDIR" -Force
cd "$OUTDIR"

& ".\$NAME.exe" -i 1 -d MyRecording -m 0
$EXIT_CODE=$LASTEXITCODE

if ($EXIT_CODE) {
    echo "*** Test failed! ***"
} else {
    echo "*** Test passed. ***"
}
deactivate
# echo $EXIT_CODE
cd ..
exit $EXIT_CODE