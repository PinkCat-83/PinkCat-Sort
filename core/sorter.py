import os
import shutil
import unicodedata

from rapidfuzz import fuzz, process


def sort_files(path, tolerance, on_progress, on_log, t):
    """
    Scan the first level of `path` and move each file into its best-matching folder.

    Parameters:
        path        -- folder to sort
        tolerance   -- minimum similarity threshold (0-100)
        on_progress -- callback(processed, total) for progress updates
        on_log      -- callback(message) for status messages
        t           -- translate callable, t(key, **kwargs) -> str

    Returns a dict with:
        moved    -- number of files moved
        ignored  -- number of files not moved
        unmoved  -- list of dicts: {file, folder, score, reason, error?}
                    reason is one of: "low_score" | "no_folders" | "py_file" | "error"
    """
    file_names = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    total = len(file_names)
    processed = 0
    moved = 0
    ignored = 0
    unmoved = []

    on_log("\n" + "=" * 50)
    on_log(t("log_start_header"))
    on_log("=" * 50)
    on_log(t("log_total_files", total=total))
    on_log(t("log_tolerance", tolerance=tolerance) + "\n")
    on_progress(0, total)

    for file_name in file_names:
        source = os.path.join(path, file_name)
        try:
            if file_name.endswith(".py"):
                unmoved.append({"file": file_name, "folder": None, "score": None, "reason": "py_file"})
                ignored += 1
            else:
                folder_name = _find_best_folder(file_name, path)
                if folder_name is None:
                    on_log(t("log_no_folders", file=file_name))
                    unmoved.append({"file": file_name, "folder": None, "score": None, "reason": "no_folders"})
                    ignored += 1
                else:
                    score = fuzz.ratio(normalize_text(file_name), normalize_text(folder_name))
                    if score >= tolerance:
                        on_log(t("log_moving", file=file_name, folder=folder_name, score=f"{score:.2f}"))
                        destination = os.path.join(path, folder_name)
                        shutil.move(source, os.path.join(destination, file_name))
                        moved += 1
                    else:
                        on_log(t("log_no_dest", file=file_name, score=f"{score:.2f}"))
                        unmoved.append({"file": file_name, "folder": folder_name, "score": score, "reason": "low_score"})
                        ignored += 1

        except Exception as e:
            unmoved.append({"file": file_name, "folder": None, "score": None, "reason": "error", "error": str(e)})
            on_log(t("log_error_file", file=file_name, error=str(e)))

        processed += 1
        on_progress(processed, total)

    on_log("\n" + "=" * 50)
    on_log(t("log_complete_header"))
    on_log("=" * 50)
    on_log(t("log_moved_count", count=moved))
    on_log(t("log_ignored_count", count=ignored))

    return {"moved": moved, "ignored": ignored, "unmoved": unmoved}


def _find_best_folder(file_name, path):
    """Return the folder name most similar to `file_name`, or None if none can be found."""
    folder_names = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    if not folder_names:
        return None
    normalized = normalize_text(file_name)
    result = process.extractOne(normalized, folder_names, scorer=fuzz.ratio)
    if result is None:
        return None
    return result[0]


def normalize_text(text):
    """Normalize a file or folder name to make fuzzy comparison more reliable."""
    if "-" in text:
        text = text.split("-", 1)[1]
    if "." in text:
        text = text.rsplit(".", 1)[0]

    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = text.lower()
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    text = text.replace(" ", "")
    text = ''.join(char for char in text if not char.isdigit())
    return text
