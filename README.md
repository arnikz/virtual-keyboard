# Virtual Keyboard
[![Windows CI](https://github.com/arnikz/virtual-keyboard/actions/workflows/ci_windows.yaml/badge.svg?branch=dev)](https://github.com/arnikz/virtual-keyboard/actions/workflows/ci_windows.yaml)

### Prerequisites
- Python
  - [Tkinter](https://docs.python.org/3.13/library/tkinter.html)
  - [AHK](https://github.com/spyoungtech/ahk)
  - [PyInstaller](https://pyinstaller.org/) - used to create one-file bundled [`Keyboard.exe`](/Resources/Keyboard.exe) from [`Keyboard.py`](/src/Keyboard.py) script

1. Open _PowerShell_ and install Python incl. dependencies.

```powershell
.\install.ps1
```

2. Create a packaged Python app.

```powershell
.\build.ps1 # output file: Resources\Keyboard.exe
```
