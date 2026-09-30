$VENV=".venv"

winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements
rm -r -force $VENV
py -m venv $VENV
& ".\$ENV\Scripts\activate"
py -m pip install "ahk[binary]" # install AutoHotkey(V2).exe binaries into $VENV
py -m pip install pyinstaller
py -c "import ahk_binary; from ahk import AHK; ahk = AHK(executable_path='$VENV\\Scripts\\AutoHotkey.exe')" # test AHK

if ($? -eq "True") {
    echo "*** Test passed. ***"
} else {
    echo "*** Test failed! ***"
}
deactivate
