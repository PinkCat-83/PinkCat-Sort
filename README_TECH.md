# 🔧 Technical README — PinkCat Sort

> Internal reference for development, debugging, and AI-assisted work.  
> → [Presentation README](./README.md)

---

## 🤖 AI Instructions

- Wait for the author to specify what needs to be done before proceeding.
- Ask for the relevant files before making any modifications.
- Matching and sorting logic lives exclusively in `core/sorter.py` — do not add it to the GUI layer.
- UI construction is in `ui/components.py` and styles in `ui/styles.py` — keep them separate.

---

## 1. Project Structure

```
PinkCat Sort/
├── PinkCat Sort.py       # Entry point
├── app.py                # Main FileSorterGUI class
├── core/
│   ├── sorter.py         # Fuzzy matching and file sorting logic
│   └── report.py         # .txt report export
└── ui/
    ├── components.py     # Interface construction
    └── styles.py         # Colors and styles
```

---

## 2. Module Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Main GUI class — wires UI components to core logic |
| `core/sorter.py` | Fuzzy name matching (`rapidfuzz`) and file move operations |
| `core/report.py` | Generates and exports the `.txt` processing log |
| `ui/components.py` | Builds all Tkinter/tkinterdnd2 widgets |
| `ui/styles.py` | Color palette and style constants |

---

## 3. Matching System

Uses `rapidfuzz` for fuzzy string comparison between filenames and folder names.

- Tolerance threshold: 0–100%, configurable via slider. **80–90% recommended.**
- Files below the threshold are not moved and appear in the unmatched section of the report.
- `.py` files are always excluded from processing.
- Only the **first level** of the selected folder is scanned — no recursion into subfolders.

---

## 4. Dependencies

| Package | Purpose |
|---|---|
| `tkinterdnd2` | Drag & drop folder support |
| `rapidfuzz` | Fast fuzzy string matching |

---

## 5. Pending Tasks

- [ ] None currently tracked
