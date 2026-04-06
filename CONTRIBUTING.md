# Contributing to crontab-ui

Thanks for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

- Open an [issue](https://github.com/ball46/crontab-ui/issues) with a clear description
- Include your OS, Python version, and steps to reproduce

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the use case and expected behavior

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes in `crontab_ui.py`
4. Run tests: `pip install -r requirements-dev.txt && python3 -m pytest tests/ -v`
5. Test manually: `python3 crontab_ui.py --lang en` and `--lang th`
6. Commit with a clear message: `git commit -m "Add: description"`
7. Push and open a Pull Request

### Code Style

- Follow PEP 8
- Keep i18n strings in the `STRINGS` dict for both `en` and `th`
- Test with both English and Thai languages

### Adding a New Language

1. Add a new key to the `STRINGS` dict in `crontab_ui.py`
2. Update `detect_lang()` to support the new language code
3. Update `--lang` choices in argparse
4. Update README with the new language

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
