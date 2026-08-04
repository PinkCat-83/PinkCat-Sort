"""
language/i18n.py — Internationalization module for PinkCat Sort.

Usage:
    from language.i18n import I18n
    t = I18n()              # loads Español by default
    t.set_language("English")
    label = t("btn_sort")
"""

import csv
import os

_DEFAULT_LANGUAGE = "Español"
_CSV_PATH = os.path.join(os.path.dirname(__file__), "translations.csv")


class I18n:
    """Translation manager backed by the semicolon-separated CSV in language/."""

    def __init__(self, language: str = _DEFAULT_LANGUAGE):
        self._translations: dict[str, dict[str, str]] = {}
        self._languages: list[str] = []
        self._language: str = language
        self._load()

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        with open(_CSV_PATH, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            self._languages = [col for col in reader.fieldnames if col != "key"]
            for row in reader:
                key = row["key"].strip()
                self._translations[key] = {
                    lang: row[lang] for lang in self._languages
                }

    # ── Public API ───────────────────────────────────────────────────────────

    @property
    def languages(self) -> list[str]:
        """List of languages available in the CSV."""
        return list(self._languages)

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, language: str) -> None:
        if language not in self._languages:
            raise ValueError(
                f"Language '{language}' is not available. "
                f"Options: {self._languages}"
            )
        self._language = language

    def __call__(self, key: str, **kwargs) -> str:
        """
        Return the translation of `key` in the active language.
        Accepts kwargs for interpolation: t("confirm_msg", name="Ana").
        Returns the key itself in brackets if it does not exist.
        """
        row = self._translations.get(key)
        if row is None:
            return f"[{key}]"
        text = row.get(self._language) or row.get(_DEFAULT_LANGUAGE, f"[{key}]")
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

    def get(self, key: str, default: str = "") -> str:
        """Like __call__ but returns `default` if the key does not exist."""
        row = self._translations.get(key)
        if row is None:
            return default
        return row.get(self._language, default)
