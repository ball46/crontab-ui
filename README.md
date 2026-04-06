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
crontab-ui -h            # show help: keybindings, supported languages, examples
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

- Click any **Preset** button in a 3-column grid (Every 5 min, Weekdays 09:00, 1st of month, etc.)
- Set **Minute**, **Hour**, **Day of Month** manually via input fields
- **Day of Week**: toggle buttons (Mon–Sun) with quick-select buttons (All / Weekdays / Weekend)
- **Month**: toggle buttons (Jan–Dec) with quick-select button (All)
- Multi-select supported — generates proper cron syntax (e.g., `1,3,5` or `3,7,12`)
- **Live preview** updates the cron expression and description in real time
- **Cron expression validation** — invalid values are rejected with a clear error before saving
- **Input sanitization** — dangerous characters (newlines, control chars) are stripped automatically
- **Catppuccin Mocha** dark theme for comfortable terminal use
- Press `Ctrl+S` to save — writes directly to crontab, no vim needed

---

## Supported Cron Syntax

### Standard 5-field format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * * /path/to/command
```

Supports: wildcards (`*`), ranges (`1-5`), steps (`*/5`, `1-30/2`), and lists (`1,3,5`)

### @-shortcut syntax

| Shortcut | Equivalent | Description |
|---|---|---|
| `@reboot` | *(run at startup)* | At system reboot |
| `@yearly` / `@annually` | `0 0 1 1 *` | Once a year (Jan 1, midnight) |
| `@monthly` | `0 0 1 * *` | Once a month (1st, midnight) |
| `@weekly` | `0 0 * * 0` | Once a week (Sunday, midnight) |
| `@daily` / `@midnight` | `0 0 * * *` | Once a day (midnight) |
| `@hourly` | `0 * * * *` | Once an hour |

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
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
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
