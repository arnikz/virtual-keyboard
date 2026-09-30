### Virtual Keyboard
- [AutoHotkey](https://www.autohotkey.com/) (AHK) only:
  - [`Keyboard.ahk`](/src/Keyboard.ahk) script to `Keyboard.exe` via [Ahk2Exe](https://github.com/AutoHotkey/Ahk2Exe)
- Python/TK + [AHK](https://github.com/spyoungtech/ahk) wrapper
  - [`Keyboard.py`](/src/Keyboard.py) script to `PyKeyboard.exe` via [PyInstaller](https://pyinstaller.org/)

1. Open _PowerShell_ and install Python incl. dependencies.

```powershell
.\install.ps1
```

2. Create a packaged Python app.

```powershell
.\build.ps1 # output file: dist\PyKeyboard.exe
```
