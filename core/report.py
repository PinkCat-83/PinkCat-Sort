from datetime import datetime


def _format_entry(entry, t) -> str:
    """Convert an unmoved-file dict into a readable line."""
    reason = entry.get("reason")
    file = entry.get("file", "?")

    if reason == "low_score":
        score = entry.get("score")
        folder = entry.get("folder", "?")
        score_str = f"{score:.1f}%" if score is not None else "?"
        return f"{file}  →  '{folder}'  ({t('report_similarity_label')}: {score_str})"
    elif reason == "py_file":
        return f"{file}  ({t('unmoved_py_file')})"
    elif reason == "error":
        return f"{file}  ❌ {entry.get('error', '')}"
    elif reason == "no_folders":
        return f"{file}  ({t('summary_no_folders')})"
    else:
        return str(entry)


def generate_report(full_log, unmoved_files, t) -> str:
    """
    Build the report content as a string.

    Parameters:
        full_log      -- list of process messages
        unmoved_files -- list of dicts describing each unmoved file
        t             -- translate callable, t(key, **kwargs) -> str
    """
    lines = []
    lines.append("=" * 70)
    lines.append(t("report_title"))
    lines.append(f"{t('report_date_label')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70 + "\n")

    lines.append(t("report_full_process"))
    lines.append("-" * 70)
    lines.extend(full_log)

    if unmoved_files:
        lines.append("\n" + "=" * 70)
        lines.append(t("report_unmoved_files"))
        lines.append("=" * 70)
        for entry in unmoved_files:
            lines.append(f"• {_format_entry(entry, t)}")

    return "\n".join(lines)


def save_report(file_path, full_log, unmoved_files, t) -> None:
    """
    Save the report to `file_path`.

    Raises an exception if the file cannot be written.
    """
    content = generate_report(full_log, unmoved_files, t)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
