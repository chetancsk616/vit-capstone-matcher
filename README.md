# Off-Campus Internship Scraper & VIT Capstone Matcher

A Streamlit dashboard that scrapes tech internships with `python-jobspy`, scores postings for VIT off-campus Capstone conversion readiness, and exports shortlisted roles.

## Features

- Dark, developer-first Streamlit dashboard
- Scrapes LinkedIn, Indeed, ZipRecruiter, and Google Jobs via `python-jobspy`
- VIT Capstone Compatibility Score from 0 to 100
- Job cards with direct application links
- Searchable Pandas data table with CSV and Excel exports
- Interactive VIT checklist for stipend, duration, reviews, guides, and NOC steps
- PyInstaller launcher and build scripts for Windows and macOS

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If pip hits a certificate issue on Windows:

```powershell
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## Build Executables

Windows:

```powershell
.\build_windows.ps1
```

macOS, from a Mac:

```bash
chmod +x build_macos.sh
./build_macos.sh
```

PyInstaller builds must be created on the target operating system. The generated Windows executable is intentionally not tracked in Git because it is larger than GitHub's normal file size limit.
