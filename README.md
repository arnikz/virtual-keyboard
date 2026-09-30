### Virtual Keyboard
- [AutoHotkey](https://www.autohotkey.com/) (AHK) only:
  - [`Keyboard.ahk`](/src/Keyboard.ahk) script to `Keyboard.exe` via [Ahk2Exe](https://github.com/AutoHotkey/Ahk2Exe)
- Python/TK + [AHK](https://github.com/spyoungtech/ahk) wrapper
  - [`Keyboard.py`](/src/Keyboard.py) script to `PyKeyboard.exe` via [PyInstaller](https://pyinstaller.org/)

1. Open _PowerShell_ and install Python incl. dependencies.
```powershell
winget install -e --id Python.Python.3.13
py -m venv .venv
.\venv\Scripts\activate
py -m pip install "ahk[binary]" # install AutoHotkey(V2).exe binaries in .\.venv\Scripts\
py -m pip install pyinstaller
python -c "import ahk_binary; from ahk import AHK; ahk = AHK(executable_path='.venv\\Scripts\\AutoHotkey.exe')" # test AHK
```

2. Create a packaged Python app.

```powershell
pyinstaller --name PyKeyboard --noconsole --onefile Keyboard.py # output file: dist/PyKeyboard.exe
cp .\.venv\Scripts\AutoHotkey.exe .\dist\
cd .\dist
.\PyKeyboard.exe # lanscape (default) or portrait mode with -p, --portrait option
```
