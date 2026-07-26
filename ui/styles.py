"""
ui/styles.py — Paleta y constantes de estilo para PinkCat Sort (CustomTkinter).

Toda la configuración visual vive aquí.  Los componentes importan desde este
módulo; ningún color o fuente se define inline en components.py.
"""

import customtkinter as ctk

# ── Apariencia global ────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")   # base que luego sobreescribimos

# ── Paleta ───────────────────────────────────────────────────────────────────

# Fondos
BG_APP         = "#1a1a2e"   # fondo raíz — azul oscuro casi negro
BG_SURFACE     = "#16213e"   # superficies elevadas (frames)
BG_CARD        = "#0f3460"   # tarjetas / paneles con contenido
BG_INPUT       = "#1e2a45"   # campos de texto y entradas
BG_DROP        = "#0d2137"   # zona de drop

# Acento principal — magenta cálido
ACCENT         = "#e91e8c"   # botón primario, resaltados
ACCENT_HOVER   = "#c91575"
ACCENT_LIGHT   = "#ff4db8"   # versión clara para hover en iconos

# Acento secundario — cian
ACCENT2        = "#00d4ff"   # progress bar, etiquetas de similitud
ACCENT2_DIM    = "#0095b3"

# Textos
TEXT_PRIMARY   = "#f0f0f8"
TEXT_SECONDARY = "#9aaccc"
TEXT_MUTED     = "#5d6f8a"

# Estados
SUCCESS        = "#00e5a0"
SUCCESS_HOVER  = "#00b87e"
ERROR          = "#ff4d6d"
WARNING        = "#ffbb33"

# Bordes
BORDER         = "#1e3a5a"
BORDER_FOCUS   = ACCENT

# ── Tipografía ───────────────────────────────────────────────────────────────

FONT_TITLE     = ("Segoe UI Semibold",  26)
FONT_SUBTITLE  = ("Segoe UI",          15)
FONT_LABEL     = ("Segoe UI",          14, "bold")
FONT_BODY      = ("Segoe UI",          13)
FONT_SMALL     = ("Segoe UI",          12)
FONT_MONO      = ("Consolas",          12)
FONT_COUNTER   = ("Segoe UI",          16, "bold")
FONT_PCT       = ("Segoe UI Semibold", 17)

# ── Radios y espaciado ───────────────────────────────────────────────────────

RADIUS_SM      = 6
RADIUS_MD      = 10
RADIUS_LG      = 14
PAD_XS         = 4
PAD_SM         = 8
PAD_MD         = 14
PAD_LG         = 20
PAD_XL         = 28


# ── Helper: badge de estado ──────────────────────────────────────────────────

def status_color(score: float, threshold: float) -> str:
    """Devuelve un color semáforo según la puntuación de similitud."""
    if score >= threshold:
        return SUCCESS
    if score >= threshold * 0.85:
        return WARNING
    return ERROR
