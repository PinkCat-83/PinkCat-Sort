# 🔧 Technical README — PinkCat Sort

> Internal reference for development, debugging, and AI-assisted work.  
> → [Presentation README](./README.md)

---

## 🤖 AI Instructions

- Wait for the author to specify what needs to be done before proceeding.
- Ask for the relevant files before making any modifications.
- Matching and sorting logic lives exclusively in `core/sorter.py` — do not add it to the GUI layer.
- UI construction is in `ui/components.py` and styles in `ui/styles.py` — keep them separate.
- All UI text must go through `app.t` (the `I18n` instance) — no hardcoded strings in the UI layer.
- Fonts must be defined as `CTkFont` objects in `ui/components.py` — never as tuples, as CustomTkinter ignores them on Windows.

---

## 1. Project Structure

```
PinkCat Sort/
├── PinkCat Sort.pyw      # Entry point (no console window)
├── app.py                # Main FileSorterGUI class
├── core/
│   ├── sorter.py         # Fuzzy matching and file sorting logic
│   └── report.py         # .txt report export
├── ui/
│   ├── components.py     # Interface construction (CustomTkinter)
│   └── styles.py         # Color palette and style constants
└── language/
    ├── i18n.py           # Internationalization module
    └── translations.csv  # Translations (semicolon-separated)
```

---

## 2. Module Responsibilities

| File | Responsibility |
|---|---|
| `PinkCat Sort.pyw` | Entry point — sets CTk appearance mode, creates root window |
| `app.py` | Main GUI class — wires UI components to core logic |
| `core/sorter.py` | Fuzzy name matching (`rapidfuzz`) and file move operations |
| `core/report.py` | Generates and exports the `.txt` processing log |
| `ui/components.py` | Builds all CustomTkinter widgets; exposes `build_ui()` and `refresh_ui_texts()` |
| `ui/styles.py` | Color palette, style constants; sets CTk dark mode on import |
| `language/i18n.py` | `I18n` class — loads CSV, exposes `t("key")` and `set_language()` |
| `language/translations.csv` | All UI strings in all supported languages |

---

## 3. Matching System

Uses `rapidfuzz` for fuzzy string comparison between filenames and folder names.

- Tolerance threshold: 0–100%, configurable via slider. **80–90% recommended.**
- Files below the threshold are not moved and appear in the unmatched section of the report.
- `.py` files are always excluded from processing.
- Only the **first level** of the selected folder is scanned — no recursion into subfolders.

`sort_files()` returns a dict with:
- `movidos` — number of files successfully moved
- `ignorados` — number of files not moved
- `no_movidos` — list of dicts: `{file, folder, score, reason, error?}`
  - `reason` values: `"low_score"` | `"no_folders"` | `"py_file"` | `"error"`

---

## 4. Internationalization (i18n)

- Translations live in `language/translations.csv` (semicolon-separated, UTF-8).
- First column is `key`; remaining columns are language names (e.g. `Español`, `English`).
- `app.t` is the active `I18n` instance, initialized before `build_ui()`.
- To add a language: add a column to the CSV — no code changes needed.
- To change language at runtime: `app.t.set_language("English")`, then `refresh_ui_texts(app)`.

---

## 5. UI — CustomTkinter notes

- Dark theme is set via `ctk.set_appearance_mode("dark")` in `PinkCat Sort.pyw`, before the root window is created.
- All fonts are `CTkFont` objects defined in `_init_fonts()` inside `components.py`. Using tuples causes CTk to silently ignore font sizes on Windows.
- `refresh_ui_texts(app)` updates all widget texts without rebuilding the UI — call it after every language change.

---

## 6. Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Modern themed UI widgets |
| `tkinterdnd2` | Drag & drop folder support |
| `rapidfuzz` | Fast fuzzy string matching |

---

## 7. Pending Tasks

- [ ] None currently tracked
