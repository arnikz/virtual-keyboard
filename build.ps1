$VENV      = ".venv"
$NAME      = "Keyboard"
$OUTDIR    = "Resources" # default: dist
$AHK_EXE   = "AutoHotkey.exe"
$MODE      = 0 # landscape (0) or portrait (1)
$EXIT_CODE = 0

function LogInfo {
    param([int]$exitCode)

    switch ($exitCode) {
        0       { Write-Host "* Success" }
        1       { Write-Host "* Generic error" }
        2       { Write-Host "* Usage error" }
        default { Write-Host "* Unknown error: $exitCode" }
    }
}

& ".\$VENV\Scripts\pyinstaller.exe" --name "$NAME" --noconsole --distpath $OUTDIR --onefile "src\Keyboard.py"

Copy-Item -Path ".\$VENV\Scripts\$AHK_EXE" -Destination "$OUTDIR" -Force

& ".\$OUTDIR\$NAME.exe" -i 1 -d MyRecording -m $MODE
$EXIT_CODE = $LASTEXITCODE
LogInfo -exitCode $EXIT_CODE

exit $EXIT_CODE