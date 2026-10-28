$VENV      = ".venv"
$NAME      = "Keyboard"
$OUTDIR    = "Resources"
$AHK_EXE   = "AutoHotkey.exe"
$MODE      = 0 # 0 = landscape or 1 = portrait
$EXIT_CODE = 0
$PAUSE     = 5 # sleep 5 sec

function LogInfo {
    param([int]$exitCode)

    switch ($exitCode) {
        0       { Write-Host "* Success" }
        1       { Write-Host "* Generic error" }
        2       { Write-Host "* Usage error" }
        default { Write-Host "* Unknown error: $exitCode" }
    }
}

# Activate venv and create exec
& ".\$VENV\Scripts\activate"
py -m nuitka --onefile --enable-plugin=tk-inter --assume-yes-for-downloads --windows-console-mode=disable --no-deployment-flag=self-execution src\Keyboard.py

# Copy exec to target dir
New-Item -Type dir ".\$OUTDIR" -Force
Copy-Item ".\$VENV\Scripts\$AHK_EXE" ".\$OUTDIR\$AHK_EXE" -Force
Move-Item ".\$NAME.exe" ".\$OUTDIR\$NAME.exe" -Force

# Run exec and log errors
$proc = Start-Process -FilePath ".\$OUTDIR\$NAME.exe" -ArgumentList "-i", "1", "-d", "MyRecording", "-m", "$MODE" -PassThru
Start-Sleep -Seconds $PAUSE
$EXIT_CODE = $proc.ExitCode
LogInfo -exitCode $EXIT_CODE
deactivate
exit $EXIT_CODE
