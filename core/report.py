from datetime import datetime


def generate_report(log_completo, archivos_no_movidos):
    """
    Genera el contenido del informe como string.

    Parámetros:
        log_completo        -- lista de mensajes del proceso
        archivos_no_movidos -- lista de archivos que no se movieron
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
        for archivo in archivos_no_movidos:
            lines.append(f"• {archivo}")

    return "\n".join(lines)


def save_report(file_path, log_completo, archivos_no_movidos):
    """
    Guarda el informe en `file_path`.

    Lanza una excepción si no se puede escribir el archivo.
    """
    content = generate_report(log_completo, archivos_no_movidos)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
