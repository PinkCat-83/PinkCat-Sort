import shutil
import os
import unicodedata
from rapidfuzz import process, fuzz


def sort_files(path, tolerancia, on_progress, on_log):
    """
    Recorre los archivos de `path` y los mueve a la carpeta más similar.

    Parámetros:
        path        -- ruta de la carpeta a ordenar
        tolerancia  -- umbral mínimo de similitud (0-100)
        on_progress -- callback(procesados, total) para actualizar el progreso
        on_log      -- callback(mensaje) para emitir mensajes de estado

    Devuelve un dict con las claves:
        movidos         -- número de archivos movidos
        ignorados       -- número de archivos no movidos
        no_movidos      -- lista de strings describiendo cada archivo no movido
    """
    file_names = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    total = len(file_names)
    procesados = 0
    movidos = 0
    ignorados = 0
    no_movidos = []

    on_log("\n" + "=" * 50)
    on_log("🚀 INICIANDO PROCESO DE ORDENACIÓN")
    on_log("=" * 50)
    on_log(f"📊 Total de archivos encontrados: {total}")
    on_log(f"⚙️ Tolerancia configurada: {tolerancia}%\n")
    on_progress(0, total)

    for file_name in file_names:
        origen = os.path.join(path, file_name)
        try:
            if file_name.endswith(".py"):
                no_movidos.append(f"{file_name} (archivo .py - ignorado)")
                ignorados += 1
            else:
                folder_name = _find_best_folder(file_name, path)
                score = fuzz.ratio(normalize_text(file_name), normalize_text(folder_name))

                score_fmt = f"{score:.2f}"
                if folder_name != "ERROR" and score >= tolerancia:
                    on_log(f"📦 Moviendo '{file_name}' → '{folder_name}' (similitud: {score_fmt}%)")
                    destino = os.path.join(path, folder_name)
                    shutil.move(origen, os.path.join(destino, file_name))
                    movidos += 1
                else:
                    on_log(f"⚠️ Sin destino para '{file_name}' (similitud: {score_fmt}%)")
                    no_movidos.append(f"{file_name} (similitud: {score_fmt}%)")
                    ignorados += 1

        except Exception as e:
            no_movidos.append(f"{file_name}: {str(e)}")
            on_log(f"❌ Error con '{file_name}': {str(e)}")

        procesados += 1
        on_progress(procesados, total)

    on_log("\n" + "=" * 50)
    on_log("✅ PROCESO COMPLETADO")
    on_log("=" * 50)
    on_log(f"📈 Archivos movidos: {movidos}")
    on_log(f"⭐ Archivos ignorados: {ignorados}")

    return {"movidos": movidos, "ignorados": ignorados, "no_movidos": no_movidos}


def _find_best_folder(file_name, path):
    """Devuelve el nombre de la carpeta más similar al archivo, o 'ERROR'."""
    folder_names = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    try:
        normalized = normalize_text(file_name)
        folder_name, _score, _ = process.extractOne(normalized, folder_names, scorer=fuzz.ratio)
        return folder_name
    except Exception:
        return "ERROR"


def normalize_text(text):
    """Normaliza un nombre de archivo o carpeta para facilitar la comparación."""
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
