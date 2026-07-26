# 🐱🌸 PinkCat Sort

Desktop application that automatically organizes files into folders using approximate name matching. Select a folder, adjust the tolerance, and let PinkCat Sort do the rest.

---

## What is this?

Students are required to include their full name in every file they submit. PinkCat Sort reads those filenames and automatically moves each file into the corresponding student's folder — even when names have small differences like typos, missing accents, or slight variations.

This serves two purposes: it saves the teacher from sorting files manually, and it reinforces a real workplace habit. Consistent file naming conventions are standard practice in professional environments — and not following them is grounds for dismissal in many companies.

---

## Features

- **Drag & drop** — drag a folder directly onto the window
- **Fuzzy matching** — matches files to folders even with small name differences
- **Configurable tolerance** — adjust the similarity threshold (0–100%) to control precision
- **Real-time progress** — progress bar and status log during sorting
- **Summary window** — after sorting, a separate window lists every unmatched file, its best candidate folder, and the similarity score
- **Export report** — saves the full log as `.txt`
- **Multi-language UI** — switch between 8 languages from the interface (Español, English, Português, Français, Deutsch, Italiano, 日本語, and Nyan 🐱)
- **`.py` files are always ignored**

---

## Requirements

- Python 3.8+
- `customtkinter`
- `tkinterdnd2`
- `rapidfuzz`

---

## Usage

1. Select a folder using the *Browse* button or drag it onto the drop zone.
2. Adjust the tolerance slider. **80–90% is recommended.**
3. Click **Ordenar Archivos**.
4. A summary window will open showing which files were moved and which weren't, with similarity details for each unmatched file.
5. Optionally export the report.

---

## Notes

- Only files in the **first level** of the selected folder are processed — subfolders are not entered.
- Files with no folder match above the threshold appear in the unmatched section of the report.
- To add a new language, simply add a column to `language/translations.csv` — no code changes needed.

---

## Technical Documentation

→ [Technical README](./README_TECH.md)
