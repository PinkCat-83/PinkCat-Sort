"""
ui/theme_loader.py
Punto único de acceso a la paleta de colores activa.

Regla de oro: ningún archivo de UI importa `ui.themes.green` /
`ui.themes.pink` / `ui.themes.pro` directamente. Siempre se llama a
get_theme().

Este archivo vive en ui/theme_loader.py (el proyecto no tiene carpeta
gui/), con las paletas en ui/themes/{green,pink,pro}.py — copiadas tal
cual desde el PinkCat Design System, sin regenerar.
"""

import importlib

DEFAULT_THEME = "pink"


def get_theme(name: str = DEFAULT_THEME) -> dict:
    """
    Devuelve el diccionario THEME del tema solicitado.
    Si el nombre no existe (typo en el JSON de config, tema borrado, etc.),
    cae de vuelta a DEFAULT_THEME en vez de lanzar una excepción.
    """
    try:
        module = importlib.import_module(f"ui.themes.{name}")
    except ModuleNotFoundError:
        module = importlib.import_module(f"ui.themes.{DEFAULT_THEME}")
    return module.THEME
