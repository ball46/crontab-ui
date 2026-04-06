# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2026-04-06

### Added
- **Cron expression validation** — minute, hour, day, month, and day-of-week fields are validated against their allowed ranges before saving. Invalid values (e.g., `60` for minute, `foo` for hour) are rejected with a clear error message in both English and Thai.
- **`@reboot` / `@daily` / `@weekly` syntax support** — `load_crontab()` now correctly parses `@reboot`, `@daily`, `@midnight`, `@weekly`, `@monthly`, `@yearly`, `@annually`, and `@hourly` entries. These are preserved in their original shortcut form when saving back.
- **Input sanitization** — newlines, null bytes, and other control characters in the command field are stripped before writing to crontab, preventing file corruption.
- **Test suite** — 54 unit and integration tests using pytest, covering validation, `@`-syntax round-trips, and sanitization.

---

## [1.2.0] - 2026-03-08

### Added
- **Help flag** (`-h` / `--help`) — shows supported languages, all keybindings, and usage examples

---

## [1.1.0] - 2026-03-07

### Changed
- New **Catppuccin Mocha** color theme for better readability and aesthetics
- Preset buttons now displayed in a **3-column horizontal grid** layout
- Day of Week selection changed from dropdown to **toggle buttons** (Mon–Sun) with quick-select (All / Weekdays / Weekend)
- Month selection changed from dropdown to **toggle buttons** (Jan–Dec) with quick-select (All)
- Supports **multi-select** for days and months (e.g., `1,3,5` or `3,7,12`)
- Removed top-bar (shortcuts now shown in Footer only)
- `Ctrl+C` changed from quit to **Copy** selected job; use `q` to quit instead

### Added
- **Copy/Paste** cron jobs (`Ctrl+C` = copy, `Ctrl+V` = paste as new job)
- **Command validation** on save — warns if command/path not found, with option to save anyway

### Fixed
- Dependency isolation using **venv** (`~/.local/share/crontab-ui/venv`) to avoid PEP 668 errors on Ubuntu 24.04+
- `install.sh` no longer exits prematurely due to `set -e` on pip install fallback

---

## [1.0.0] - 2026-03-07

### Added
- Interactive TUI for managing crontab using [Textual](https://github.com/Textualize/textual)
- Add, edit, delete cron jobs with live preview
- Preset buttons for common schedules (every 5 min, daily, weekdays, etc.)
- Human-readable cron description
- Bilingual support: English and Thai (ภาษาไทย)
- Language detection from `--lang` flag, `CRONTAB_UI_LANG` env, or system locale
- One-liner installer with auto Python installation
- Auto-install `textual` dependency on first run
- Supported OS: Ubuntu, Debian, Fedora, Arch, macOS
