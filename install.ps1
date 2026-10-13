$VENV = ".venv"

winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements
Remove-Item -Path $VENV -Recurse -Force -ErrorAction SilentlyContinue
py -m venv $VENV
& ".\$VENV\Scripts\activate"
py -m pip install -r requirements.txt
py -c "import ahk_binary; from ahk import AHK; ahk = AHK(executable_path='$VENV\\Scripts\\AutoHotkey.exe')" # test AHK
$EXIT_CODE = $LASTEXITCODE

if ($EXIT_CODE) {
    echo "*** Test failed! ***"
}
else {
    echo "*** Test passed. ***"
}
deactivate
# echo $EXIT_CODE
exit $EXIT_CODE
