from datetime import datetime


def _format_entry(entry) -> str:
    """Convierte un dict de archivo no movido en una línea legible."""
    reason = entry.get("reason")
    file   = entry.get("file", "?")

    if reason == "low_score":
        score  = entry.get("score")
        folder = entry.get("folder", "?")
        score_str = f"{score:.1f}%" if score is not None else "?"
        return f"{file}  →  '{folder}'  (similitud: {score_str})"
    elif reason == "py_file":
        return f"{file}  (archivo .py — ignorado)"
    elif reason == "error":
        return f"{file}  ❌ {entry.get('error', '')}"
    elif reason == "no_folders":
        return f"{file}  (sin carpetas disponibles)"
    else:
        return str(entry)


def generate_report(log_completo, archivos_no_movidos):
    """
    Genera el contenido del informe como string.

    Parámetros:
        log_completo        -- lista de mensajes del proceso
        archivos_no_movidos -- lista de dicts describiendo cada archivo no movido
    """
    lines = []
    lines.append("=" * 70)
    lines.append("REPORTE DE ORDENACIÓN DE ARCHIVOS")
    lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70 + "\n")

    lines.append("PROCESO COMPLETO:")
    lines.append("-" * 70)
    lines.extend(log_completo)

    if archivos_no_movidos:
        lines.append("\n" + "=" * 70)
        lines.append("ARCHIVOS NO MOVIDOS:")
        lines.append("=" * 70)
        for entry in archivos_no_movidos:
            lines.append(f"• {_format_entry(entry)}")

    return "\n".join(lines)


def save_report(file_path, log_completo, archivos_no_movidos):
    """
    Guarda el informe en `file_path`.

    Lanza una excepción si no se puede escribir el archivo.
    """
    content = generate_report(log_completo, archivos_no_movidos)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
