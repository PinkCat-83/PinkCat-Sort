# 🔧 Technical README — PinkCat Sort

> Internal reference for development, debugging, and AI-assisted work.  
> → [Presentation README](./README.md)

---

## 🤖 AI Instructions

- Wait for the author to specify what needs to be done before proceeding.
- Ask for the relevant files before making any modifications.
- Matching and sorting logic lives exclusively in `core/sorter.py` — do not add it to the GUI layer.
- UI construction is in `ui/components.py` and styles in `ui/styles.py` — keep them separate.
- All UI text must go through `app.t` (the `I18n` instance) — no hardcoded strings in the UI layer. `core/sorter.py` and `core/report.py` receive `t` as a parameter instead of importing `I18n` themselves, so they stay decoupled from the UI.
- Colors must never be hardcoded in UI files — always read from `ui/styles.py`, which sources them from `ui/theme_loader.get_theme()`.
- `ui/theme_loader.py` and `ui/themes/{green,pink,pro}.py` are copied verbatim from the shared PinkCat Design System reference — do not regenerate or hand-edit their palette values (their Spanish comments are intentional, kept as in the source of truth).
- Fonts must be defined as `CTkFont` objects in `ui/components.py` — never as tuples, as CustomTkinter ignores them on Windows.
- All code additions (methods, variables, comments, strings) must be written in English. Do not introduce any hardcoded text in any other language — user-facing text goes through `language/translations.csv` instead.
- The active config path is `%APPDATA%\PinkCatSort\config.json` — do not hardcode paths; use `core/config.py`.

---

## 1. Project Structure

```
PinkCat Sort/
├── PinkCat Sort.pyw      # Entry point (no console window)
├── app.py                # Main FileSorterGUI class
├── core/
│   ├── config.py         # Externalized settings (%APPDATA%\PinkCatSort\config.json)
│   ├── sorter.py         # Fuzzy matching and file sorting logic
│   └── report.py         # .txt report export
├── ui/
│   ├── components.py     # Interface construction (CustomTkinter)
│   ├── styles.py         # Style constants, sourced from the active theme
│   ├── theme_loader.py   # get_theme(name) — single access point to a theme's palette
│   └── themes/
│       ├── green.py      # Green theme palette
│       ├── pink.py       # Pink theme palette (default)
│       └── pro.py        # Professional (light) theme palette
├── language/
│   ├── i18n.py           # Internationalization module
│   └── translations.csv  # Translations (semicolon-separated)
└── ico/
    ├── PinkCat-Sort.ico  # Window/taskbar icon
    ├── PinkCat-Sort.png  # Window/taskbar icon (PNG)
    └── PinkCat-Logo.png  # Mascot logo shown in the title bar
```

---

## 2. Module Responsibilities

| File | Responsibility |
|---|---|
| `PinkCat Sort.pyw` | Entry point — creates the root window |
| `app.py` | Main GUI class — wires UI components to core logic, loads config/icon/logo |
| `core/config.py` | Loads/saves `%APPDATA%\PinkCatSort\config.json` (theme, language) atomically |
| `core/sorter.py` | Fuzzy name matching (`rapidfuzz`) and file move operations |
| `core/report.py` | Generates and exports the `.txt` processing log |
| `ui/components.py` | Builds all CustomTkinter widgets and the Settings menu; exposes `build_ui()` and `refresh_ui_texts()` |
| `ui/styles.py` | Style constants sourced from the active theme; no hardcoded colors |
| `ui/theme_loader.py` | `get_theme(name)` — single point of access to a theme's color dict |
| `ui/themes/*.py` | Theme palettes (`THEME` dict), copied verbatim from the PinkCat Design System |
| `language/i18n.py` | `I18n` class — loads CSV, exposes `t("key")` and `set_language()` |
| `language/translations.csv` | All UI strings in all supported languages |

---

## 3. Matching System

Uses `rapidfuzz` for fuzzy string comparison between filenames and folder names.

- Tolerance threshold: 0–100%, configurable via slider. **80–90% recommended.**
- Files below the threshold are not moved and appear in the unmatched section of the report.
- `.py` files are always excluded from processing.
- Only the **first level** of the selected folder is scanned — no recursion into subfolders.

`sort_files(path, tolerance, on_progress, on_log, t)` returns a dict with:
- `moved` — number of files successfully moved
- `ignored` — number of files not moved
- `unmoved` — list of dicts: `{file, folder, score, reason, error?}`
  - `reason` values: `"low_score"` | `"no_folders"` | `"py_file"` | `"error"`

The `t` parameter is a translate callable (`t(key, **kwargs) -> str`), injected by the caller so `core/sorter.py` never imports `I18n` directly.

---

## 4. Internationalization (i18n)

- Translations live in `language/translations.csv` (semicolon-separated, UTF-8).
- First column is `key`; remaining columns are language names (e.g. `Español`, `English`).
- `app.t` is the active `I18n` instance, initialized before `build_ui()`, seeded from the saved language in `config.json`.
- To add a language: add a column to the CSV — no code changes needed.
- To change language at runtime: pick it from the **Settings → Language** menu, which calls `app.t.set_language(...)`, persists it to `config.json`, then calls `refresh_ui_texts(app)`.
- Language changes apply instantly, without restarting — every widget with text is refreshed in place. Theme changes require a restart (see §5).

---

## 5. Theming — PinkCat Design System

- `ui/theme_loader.get_theme(name)` is the single access point to a theme's color dict (`bg`, `panel`, `card`, `card_hover`, `border`, `accent`, `accent_dim`, `success`, `danger`, `warning`, `info`, `text`, `text_dim`, `text_muted`, `corner_radius_card`, `corner_radius_btn`).
- `ui/styles.py` reads the active theme name from `config.json` at import time and re-exports it as this project's style constants — no other file imports `ui.themes.*` directly.
- Default theme is `pink`. Available themes: `pink`, `green`, `pro` (light).
- `success` / `danger` / `warning` / `info` are identical between `green` and `pink` by design — status colors never derive from `accent`, so a given state (ok/error/warning) always reads the same regardless of brand color.
- Theme is selected from **Settings → Theme**; changing it saves the choice and shows a restart notice (color re-theming is not applied live, by design — see PinkCat Design System §10).
- Font family follows the active theme (Consolas for Green/Pink, Segoe UI for Pro); absolute sizes are this project's own, defined in `ui/components.py`.
- Window size (`WINDOW_WIDTH`, `WINDOW_HEIGHT` in `app.py`) is a project constant, independent of the theme.

---

## 6. System Config (`%APPDATA%\PinkCatSort\config.json`)

Stored at `%APPDATA%\PinkCatSort\config.json`. Created automatically on first save (e.g. first language or theme change). Independent of where the app is installed.

```json
{
  "theme": "pink",
  "language": "Español"
}
```

PinkCat Sort has no domain data file whose location the user needs to choose (unlike apps such as GitManager) — this config only holds small UI preferences. If the file is missing or a key is absent, `core/config.load_config()` falls back to `{"theme": "pink", "language": "Español"}`. Writes are atomic (`.tmp` + `os.replace()`).

---

## 7. UI — CustomTkinter notes

- Appearance mode (dark/light) is set in `ui/styles.py` based on the active theme (`pro` is light, `green`/`pink` are dark) — do not call `ctk.set_appearance_mode()` elsewhere.
- All fonts are `CTkFont` objects defined in `_init_fonts()` inside `components.py`. Using tuples causes CTk to silently ignore font sizes on Windows.
- `refresh_ui_texts(app)` updates all widget texts (including the Settings menu labels) without rebuilding the UI — call it after every language change.
- The Settings menu (native `tk.Menu`) lives at the top of the window and holds the Language and Theme selectors, per the Design System's layout convention — no loose controls in the header besides the title and the PinkCat logo.

---

## 8. Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Modern themed UI widgets |
| `tkinterdnd2` | Drag & drop folder support |
| `rapidfuzz` | Fast fuzzy string matching |
| `pillow` | Loads the PinkCat mascot logo (`ico/PinkCat-Logo.png`) as a `CTkImage` |

---

## 9. Pending Tasks

- [ ] None currently tracked
