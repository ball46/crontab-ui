# Changelog

All notable changes to this project will be documented in this file.

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
