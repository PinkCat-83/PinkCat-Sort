"""
core/config.py — Externalized settings for PinkCat Sort.

PinkCat Sort has no domain data file whose location the user needs to
choose (unlike GitManager's projects.json) — it only remembers small UI
preferences (theme, language). Those still live outside the synced project
folder, at %APPDATA%\\PinkCatSort\\config.json, and are written atomically.
"""

import json
import os

APP_FOLDER_NAME = "PinkCatSort"
CONFIG_FILE_NAME = "config.json"

DEFAULT_THEME = "pink"
DEFAULT_LANGUAGE = "Español"

_DEFAULTS = {
    "theme": DEFAULT_THEME,
    "language": DEFAULT_LANGUAGE,
}


def _config_dir() -> str:
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    return os.path.join(base, APP_FOLDER_NAME)


def _config_path() -> str:
    return os.path.join(_config_dir(), CONFIG_FILE_NAME)


def load_config() -> dict:
    """Load settings from %APPDATA%\\PinkCatSort\\config.json, falling back to defaults."""
    config = dict(_DEFAULTS)
    path = _config_path()
    if not os.path.isfile(path):
        return config
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return config
    for key in _DEFAULTS:
        if key in data:
            config[key] = data[key]
    return config


def save_config(config: dict) -> None:
    """Atomically persist settings to %APPDATA%\\PinkCatSort\\config.json."""
    directory = _config_dir()
    os.makedirs(directory, exist_ok=True)
    path = _config_path()
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)
