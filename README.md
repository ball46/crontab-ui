# crontab-ui

Interactive TUI for managing crontab — no syntax memorization, no vim required.

![Python](https://img.shields.io/badge/python-3.8+-blue) ![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey) ![License](https://img.shields.io/badge/license-MIT-green)

> 🇹🇭 รองรับภาษาไทย — Thai language supported

---

## Installation

### Option 1 — One-liner (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/ball46/crontab-ui/main/install.sh | bash
```

The installer handles everything automatically:
- Checks if Python is installed — **installs it if missing** (Ubuntu, Debian, Fedora, Arch, macOS)
- Creates an **isolated virtual environment** (`~/.local/share/crontab-ui/venv`)
- Installs `textual` inside the venv — no system packages affected
- Downloads the script from GitHub
- Adds `~/.local/bin` to PATH

### Option 2 — Clone and install

```bash
git clone https://github.com/ball46/crontab-ui.git
cd crontab-ui
chmod +x install.sh && ./install.sh
```

---

## Usage

```bash
crontab-ui               # auto-detect language from system locale
crontab-ui --lang en     # force English
crontab-ui --lang th     # force Thai (ภาษาไทย)
CRONTAB_UI_LANG=en crontab-ui   # via environment variable
```

Language priority: `--lang` flag → `CRONTAB_UI_LANG` env → system `LANG` → default English

---

## Main Screen

Displays all existing cron jobs loaded from your current crontab, with a human-readable description column.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📋 Crontab Manager    n=New  e=Edit  Del=Delete  r=Reload  q=Quit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Minute │ Hour │ Day(M) │ Month │ Day(W) │ Command         │ Description
────────┼──────┼────────┼───────┼────────┼─────────────────┼──────────────────
 0      │ 9    │ *      │ *     │ 1-5    │ /backup.sh      │ Weekdays at 09:00
 */5    │ *    │ *      │ *     │ *      │ /check.py       │ Every 5 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ✅ Loaded — 2 job(s)
```

---

## Keyboard Shortcuts

### Main screen

| Key     | Action                          |
|---------|---------------------------------|
| `n`     | Add a new cron job              |
| `e`     | Edit selected job               |
| `Del`   | Delete selected job (with confirm) |
| `r`     | Reload crontab from system      |
| `q`     | Quit                            |

### Editor screen

| Key      | Action                              |
|----------|-------------------------------------|
| `Ctrl+S` | Save and write to crontab immediately |
| `Esc`    | Cancel                              |

---

## Editor Screen

- Click any **Preset** button (Every 5 min, Weekdays 09:00, 1st of month, etc.)
- Or set each field manually (minute / hour / day / month / day of week)
- **Live preview** updates the cron expression and description in real time
- Press `Ctrl+S` to save — writes directly to crontab, no vim needed

---

## Requirements

| Requirement | Notes |
|---|---|
| Python 3.8+ | Auto-installed if missing |
| [textual](https://github.com/Textualize/textual) | Auto-installed on first run |
| Linux / macOS | Requires the `crontab` command |

---

## Supported OS

| OS | Package Manager | Notes |
|---|---|---|
| Ubuntu / Debian / Mint | `apt` | Supports deadsnakes PPA for Python 3.13 |
| Fedora / RHEL / Rocky | `dnf` | |
| Arch / Manjaro | `pacman` | |
| macOS | `brew` | Requires Homebrew |

---

## Files

```
crontab-ui/
├── crontab_ui.py     # main app (Textual TUI) — EN/TH i18n built-in
├── install.sh        # installer — one-liner + auto Python install
├── LICENSE           # MIT License
├── CONTRIBUTING.md   # contribution guidelines
├── CHANGELOG.md      # version history
├── .gitignore
└── README.md
```

---

## License

This project is licensed under the [MIT License](LICENSE).
