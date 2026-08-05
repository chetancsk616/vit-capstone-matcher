# VIT Capstone Matcher Executable Builds

## Windows
A Windows executable has already been built in this workspace:

```powershell
.\outputs\VITCapstoneMatcher.exe
```

To rebuild it on Windows:

```powershell
.\build_windows.ps1
```

The rebuilt file will appear at:

```text
dist\VITCapstoneMatcher.exe
```

## macOS
Build the macOS executable on a Mac. PyInstaller cannot reliably cross-compile a macOS binary from Windows.

```bash
chmod +x build_macos.sh
./build_macos.sh
```

The macOS build will appear at:

```text
dist/VITCapstoneMatcher
```

## How it runs
The executable starts a local Streamlit server on the first available port from 8501 and opens the dashboard in your default browser.
