"""
ui/styles.py — Style constants for PinkCat Sort (CustomTkinter).

Colors come exclusively from the active PinkCat Design System theme
(ui/theme_loader.get_theme), selected via the externalized config
(core/config.load_config). No color is hardcoded here; only layout
constants (padding, window-specific radii) that are this project's own
and intentionally live outside the theme.
"""

import customtkinter as ctk

from core.config import load_config
from ui.theme_loader import get_theme

ctk.set_appearance_mode("light" if load_config()["theme"] == "pro" else "dark")
ctk.set_default_color_theme("blue")  # base overridden below by the active theme

_config = load_config()
_theme_name = _config["theme"]
_THEME = get_theme(_theme_name)

# ── Palette (sourced from the active theme) ─────────────────────────────────

BG_APP         = _THEME["bg"]
BG_SURFACE     = _THEME["panel"]
BG_CARD        = _THEME["card"]
BG_INPUT       = _THEME["card_hover"]
BG_DROP        = _THEME["bg"]

ACCENT         = _THEME["accent"]
ACCENT_DIM     = _THEME["accent_dim"]
ACCENT_HOVER   = _THEME["accent"]
ACCENT_LIGHT   = _THEME["accent"]

ACCENT2        = _THEME["info"]  # secondary/informational highlight color

TEXT_PRIMARY   = _THEME["text"]
TEXT_SECONDARY = _THEME["text_dim"]
TEXT_MUTED     = _THEME["text_muted"]

SUCCESS        = _THEME["success"]
SUCCESS_HOVER  = _THEME["success"]
ERROR          = _THEME["danger"]
WARNING        = _THEME["warning"]

BORDER         = _THEME["border"]

# ── Typography ───────────────────────────────────────────────────────────────
# Font family follows the active theme (Consolas for Green/Pink, Segoe UI for
# Pro); absolute sizes are this project's own choice, outside the theme.

FONT_FAMILY_TITLE = "Segoe UI Semibold" if _theme_name == "pro" else "Consolas"
FONT_FAMILY_UI     = "Segoe UI"
FONT_FAMILY_MONO   = "Consolas"

# ── Radii and spacing ────────────────────────────────────────────────────────
# Card/button radii come from the theme. RADIUS_LG is a project-specific
# layout radius for large outer panels (header, drop zone) — not one of the
# two theme-defined radii, so it stays outside the theme by design.

RADIUS_SM      = _THEME["corner_radius_btn"]
RADIUS_MD      = _THEME["corner_radius_card"]
RADIUS_LG      = _THEME["corner_radius_card"] + 4

PAD_XS         = 4
PAD_SM         = 8
PAD_MD         = 14
PAD_LG         = 20
PAD_XL         = 28


# ── Helper: status badge ─────────────────────────────────────────────────────

def status_color(score: float, threshold: float) -> str:
    """Return a traffic-light color for a similarity score against a threshold."""
    if score >= threshold:
        return SUCCESS
    if score >= threshold * 0.85:
        return WARNING
    return ERROR
