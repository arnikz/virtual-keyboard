# Virtual Keyboard
[![Windows CI](https://github.com/arnikz/virtual-keyboard/actions/workflows/ci_windows.yaml/badge.svg?branch=dev)](https://github.com/arnikz/virtual-keyboard/actions/workflows/ci_windows.yaml)

### Prerequisites
- Python/TK + [AHK](https://github.com/spyoungtech/ahk) wrapper
  - [`Keyboard.py`](/src/Keyboard.py) script to `Keyboard.exe` via [PyInstaller](https://pyinstaller.org/)

1. Open _PowerShell_ and install Python incl. dependencies.

```powershell
.\install.ps1
```

2. Create a packaged Python app.

```powershell
.\build.ps1 # output file: dist\Keyboard.exe
```
