"""
ui/components.py — Construcción de la interfaz de PinkCat Sort con CustomTkinter.

Reglas de arquitectura (ver README_TECH.md):
  · Este módulo sólo construye widgets y los asocia a `app`.
  · La lógica de matching/sorting vive exclusivamente en core/sorter.py.
  · Los estilos y colores provienen de ui/styles.py.
  · Los textos provienen de app.t (instancia de language.i18n.I18n).
"""

import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from ui.styles import (
    BG_APP, BG_SURFACE, BG_CARD, BG_INPUT, BG_DROP,
    ACCENT, ACCENT_HOVER, ACCENT_LIGHT, ACCENT2,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    SUCCESS, SUCCESS_HOVER, ERROR,
    BORDER,
    RADIUS_SM, RADIUS_MD, RADIUS_LG,
    PAD_XS, PAD_SM, PAD_MD, PAD_LG,
)

# ── Fuentes como CTkFont (único método fiable en Windows) ────────────────────
# Se crean aquí a nivel de módulo; CTkFont requiere que Tk exista, así que se
# instancian en build_ui() la primera vez y se guardan en este dict.
_F = {}

def _init_fonts():
    if _F:
        return
    _F["title"]    = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
    _F["subtitle"] = ctk.CTkFont(family="Segoe UI", size=16)
    _F["label"]    = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
    _F["body"]     = ctk.CTkFont(family="Segoe UI", size=15)
    _F["small"]    = ctk.CTkFont(family="Segoe UI", size=14)
    _F["mono"]     = ctk.CTkFont(family="Consolas",  size=14)
    _F["pct"]      = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
    _F["lang"]     = ctk.CTkFont(family="Segoe UI", size=16)


# ── Helpers internos ─────────────────────────────────────────────────────────

def _frame(parent, fg=BG_SURFACE, **kw):
    return ctk.CTkFrame(parent, fg_color=fg, **kw)


def _label(parent, text, font_key="body", color=TEXT_PRIMARY, **kw):
    return ctk.CTkLabel(parent, text=text, font=_F[font_key], text_color=color, **kw)


def _separator(parent):
    return tk.Frame(parent, bg=BORDER, height=1)


# ── Punto de entrada principal ───────────────────────────────────────────────

def build_ui(app):
    _init_fonts()
    t    = app.t
    root = app.root

    root.configure(bg=BG_APP)
    root.option_add("*tearOff", False)

    wrapper = _frame(root, fg=BG_APP)
    wrapper.pack(fill=tk.BOTH, expand=True, padx=PAD_LG, pady=PAD_LG)

    _build_header(app, wrapper, t)

    body = _frame(wrapper, fg=BG_APP)
    body.pack(fill=tk.BOTH, expand=True, pady=(PAD_MD, 0))
    body.columnconfigure(0, weight=2, minsize=380)
    body.columnconfigure(1, weight=3)
    body.rowconfigure(0, weight=1)

    left = _frame(body, fg=BG_APP)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, PAD_MD))

    right = _frame(body, fg=BG_APP)
    right.grid(row=0, column=1, sticky="nsew")
    right.rowconfigure(2, weight=1)
    right.rowconfigure(4, weight=1)

    _build_left(app, left, t)
    _build_right(app, right, t)


# ── Cabecera ─────────────────────────────────────────────────────────────────

def _build_header(app, parent, t):
    header = _frame(parent, fg=BG_SURFACE, corner_radius=RADIUS_LG)
    header.pack(fill=tk.X, pady=(0, PAD_MD))

    inner = _frame(header, fg=BG_SURFACE)
    inner.pack(fill=tk.BOTH, expand=True, padx=PAD_LG, pady=PAD_MD)

    left_h = _frame(inner, fg=BG_SURFACE)
    left_h.pack(side=tk.LEFT, fill=tk.Y)

    title_col = _frame(left_h, fg=BG_SURFACE)
    title_col.pack(side=tk.LEFT)

    app._lbl_title = _label(title_col, t("app_title"), font_key="title", color=TEXT_PRIMARY)
    app._lbl_title.pack(anchor=tk.W)

    app._lbl_subtitle = _label(title_col, t("app_subtitle"), font_key="subtitle", color=TEXT_SECONDARY)
    app._lbl_subtitle.pack(anchor=tk.W, pady=(2, 0))

    right_h = _frame(inner, fg=BG_SURFACE)
    right_h.pack(side=tk.RIGHT)

    app._lbl_lang = _label(right_h, t("lang_selector_label"), font_key="small", color=TEXT_MUTED)
    app._lbl_lang.pack(anchor=tk.E)

    app.lang_var = tk.StringVar(value=app.t.language)
    app._lang_menu = ctk.CTkOptionMenu(
        right_h,
        values=app.t.languages,
        variable=app.lang_var,
        command=app._on_language_change,
        width=220,
        height=40,
        fg_color=BG_CARD,
        button_color=ACCENT,
        button_hover_color=ACCENT_HOVER,
        text_color=TEXT_PRIMARY,
        font=_F["lang"],
        dropdown_font=_F["lang"],
        dropdown_fg_color=BG_SURFACE,
        dropdown_hover_color=BG_CARD,
        dropdown_text_color=TEXT_PRIMARY,
        corner_radius=RADIUS_SM,
    )
    app._lang_menu.pack(pady=(4, 0))


# ── Columna izquierda ────────────────────────────────────────────────────────

def _build_left(app, parent, t):
    # Drop zone
    drop_card = _frame(parent, fg=BG_DROP, corner_radius=RADIUS_LG)
    drop_card.pack(fill=tk.X, pady=(0, PAD_MD))
    drop_card.configure(height=120)
    drop_card.pack_propagate(False)

    drop_card.drop_target_register(DND_FILES)
    drop_card.dnd_bind("<<Drop>>", app.on_drop)

    drop_inner = _frame(drop_card, fg=BG_DROP)
    drop_inner.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    ctk.CTkLabel(
        drop_inner, text="🗂️",
        font=ctk.CTkFont(family="Segoe UI Emoji", size=28),
        text_color=ACCENT2
    ).pack()

    app._lbl_drop = _label(drop_inner, t("drop_zone_hint"), font_key="small", color=TEXT_MUTED, justify=tk.CENTER)
    app._lbl_drop.pack(pady=(4, 0))

    # Ruta seleccionada
    app._lbl_folder = _label(parent, t("folder_selected_label"), font_key="small", color=TEXT_MUTED)
    app._lbl_folder.pack(anchor=tk.W, pady=(0, PAD_XS))

    app._entry_path = ctk.CTkEntry(
        parent,
        textvariable=app.path_to_sort,
        state="readonly",
        font=_F["small"],
        fg_color=BG_INPUT,
        border_color=BORDER,
        text_color=TEXT_SECONDARY,
        corner_radius=RADIUS_SM,
        height=34,
    )
    app._entry_path.pack(fill=tk.X, pady=(0, PAD_SM))

    # Botón Examinar
    app._btn_browse = ctk.CTkButton(
        parent,
        text=t("btn_browse"),
        command=app.browse_folder,
        fg_color=BG_CARD,
        hover_color=BG_SURFACE,
        text_color=ACCENT2,
        border_color=BORDER,
        border_width=1,
        font=_F["body"],
        corner_radius=RADIUS_SM,
        height=36,
    )
    app._btn_browse.pack(fill=tk.X, pady=(0, PAD_LG))

    _separator(parent).pack(fill=tk.X, pady=(0, PAD_LG))

    # Configuración tolerancia
    config_card = _frame(parent, fg=BG_SURFACE, corner_radius=RADIUS_LG)
    config_card.pack(fill=tk.X, pady=(0, PAD_LG))

    cfg_inner = _frame(config_card, fg=BG_SURFACE)
    cfg_inner.pack(fill=tk.BOTH, padx=PAD_MD, pady=PAD_MD)

    app._lbl_config = _label(cfg_inner, t("section_config"), font_key="label", color=ACCENT2)
    app._lbl_config.pack(anchor=tk.W, pady=(0, PAD_SM))

    app._lbl_tolerance = _label(cfg_inner, t("tolerance_label"), font_key="body", color=TEXT_PRIMARY)
    app._lbl_tolerance.pack(anchor=tk.W)

    app._lbl_tol_hint = _label(
        cfg_inner, t("tolerance_hint"),
        font_key="small", color=TEXT_MUTED, justify=tk.LEFT, wraplength=340
    )
    app._lbl_tol_hint.pack(anchor=tk.W, pady=(2, PAD_SM))

    slider_row = _frame(cfg_inner, fg=BG_SURFACE)
    slider_row.pack(fill=tk.X)

    app._slider = ctk.CTkSlider(
        slider_row,
        from_=0, to=100,
        variable=app.tolerancia,
        progress_color=ACCENT,
        button_color=ACCENT,
        button_hover_color=ACCENT_LIGHT,
        fg_color=BG_INPUT,
        corner_radius=4,
        height=16,
    )
    app._slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, PAD_SM))

    app.tolerance_label = _label(slider_row, "80%", font_key="pct", color=ACCENT)
    app.tolerance_label.pack(side=tk.RIGHT, anchor=tk.CENTER)
    app.tolerancia.trace_add("write", app.update_tolerance_label)

    _separator(parent).pack(fill=tk.X, pady=(0, PAD_LG))

    # Botón Ordenar
    app.sort_btn = ctk.CTkButton(
        parent,
        text=t("btn_sort"),
        command=app.start_sorting,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        text_color="#ffffff",
        font=_F["label"],
        corner_radius=RADIUS_MD,
        height=46,
    )
    app.sort_btn.pack(fill=tk.X)


# ── Columna derecha ───────────────────────────────────────────────────────────

def _build_right(app, parent, t):
    # Progreso
    prog_card = _frame(parent, fg=BG_SURFACE, corner_radius=RADIUS_LG)
    prog_card.pack(fill=tk.X, pady=(0, PAD_MD))
    prog_inner = _frame(prog_card, fg=BG_SURFACE)
    prog_inner.pack(fill=tk.BOTH, padx=PAD_MD, pady=PAD_MD)

    prog_header = _frame(prog_inner, fg=BG_SURFACE)
    prog_header.pack(fill=tk.X, pady=(0, PAD_SM))

    app._lbl_progress_title = _label(prog_header, t("section_progress"), font_key="label", color=TEXT_SECONDARY)
    app._lbl_progress_title.pack(side=tk.LEFT)

    app.progress_label = _label(
        prog_header,
        t("progress_count", done=0, total=0),
        font_key="small", color=TEXT_MUTED
    )
    app.progress_label.pack(side=tk.RIGHT)

    app.progress_bar = ctk.CTkProgressBar(
        prog_inner,
        progress_color=ACCENT2,
        fg_color=BG_INPUT,
        corner_radius=4,
        height=10,
    )
    app.progress_bar.set(0)
    app.progress_bar.pack(fill=tk.X)

    # Panel de estado
    _separator(parent).pack(fill=tk.X, pady=(0, PAD_MD))

    status_lbl_row = _frame(parent, fg=BG_APP)
    status_lbl_row.pack(fill=tk.X, pady=(0, PAD_XS))

    app._lbl_status_section = _label(status_lbl_row, t("section_status"), font_key="label", color=TEXT_SECONDARY)
    app._lbl_status_section.pack(anchor=tk.W)

    status_card = _frame(parent, fg=BG_CARD, corner_radius=RADIUS_MD)
    status_card.pack(fill=tk.BOTH, expand=True, pady=(0, PAD_MD))

    status_inner = _frame(status_card, fg=BG_CARD)
    status_inner.pack(fill=tk.BOTH, expand=True, padx=PAD_SM, pady=PAD_SM)

    app.status_text = tk.Text(
        status_inner,
        state="disabled",
        wrap=tk.WORD,
        font=("Consolas", 14),
        bg=BG_CARD,
        fg=TEXT_PRIMARY,
        insertbackground=TEXT_PRIMARY,
        selectbackground=ACCENT,
        relief=tk.FLAT,
        borderwidth=0,
        spacing3=4,
    )
    app.status_text.tag_configure("error",   foreground=ERROR)
    app.status_text.tag_configure("success", foreground=SUCCESS)
    app.status_text.tag_configure("accent",  foreground=ACCENT2)
    app.status_text.tag_configure("muted",   foreground=TEXT_MUTED)

    scrollbar_s = ctk.CTkScrollbar(
        status_inner, command=app.status_text.yview,
        fg_color=BG_CARD, button_color=BORDER, button_hover_color=ACCENT
    )
    scrollbar_s.pack(side=tk.RIGHT, fill=tk.Y)
    app.status_text.config(yscrollcommand=scrollbar_s.set)
    app.status_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    # Panel archivos no movidos (oculto hasta resultados)
    app._lbl_unmoved_section = _label(parent, t("section_unmoved"), font_key="label", color=TEXT_SECONDARY)

    app.results_frame = _frame(parent, fg=BG_CARD, corner_radius=RADIUS_MD)

    unmoved_inner = _frame(app.results_frame, fg=BG_CARD)
    unmoved_inner.pack(fill=tk.BOTH, expand=True, padx=PAD_SM, pady=PAD_SM)

    app.unmoved_text = tk.Text(
        unmoved_inner,
        height=6,
        state="disabled",
        wrap=tk.WORD,
        font=("Consolas", 14),
        bg=BG_CARD,
        fg=ERROR,
        insertbackground=TEXT_PRIMARY,
        relief=tk.FLAT,
        borderwidth=0,
    )
    scrollbar_u = ctk.CTkScrollbar(
        unmoved_inner, command=app.unmoved_text.yview,
        fg_color=BG_CARD, button_color=BORDER, button_hover_color=ACCENT
    )
    scrollbar_u.pack(side=tk.RIGHT, fill=tk.Y)
    app.unmoved_text.config(yscrollcommand=scrollbar_u.set)
    app.unmoved_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    app.export_btn = ctk.CTkButton(
        app.results_frame,
        text=t("btn_export"),
        command=app.export_report,
        fg_color=SUCCESS,
        hover_color=SUCCESS_HOVER,
        text_color="#ffffff",
        font=_F["label"],
        corner_radius=RADIUS_MD,
        height=40,
    )
    app.export_btn.pack(fill=tk.X, padx=PAD_SM, pady=(PAD_SM, PAD_SM))


# ── Refresco i18n ─────────────────────────────────────────────────────────────

def refresh_ui_texts(app):
    t = app.t

    app._lbl_title.configure(text=t("app_title"))
    app._lbl_subtitle.configure(text=t("app_subtitle"))
    app._lbl_lang.configure(text=t("lang_selector_label"))

    app._lbl_drop.configure(text=t("drop_zone_hint"))
    app._lbl_folder.configure(text=t("folder_selected_label"))
    app._btn_browse.configure(text=t("btn_browse"))
    app._lbl_config.configure(text=t("section_config"))
    app._lbl_tolerance.configure(text=t("tolerance_label"))
    app._lbl_tol_hint.configure(text=t("tolerance_hint"))
    app.sort_btn.configure(text=t("btn_sort"))

    app._lbl_progress_title.configure(text=t("section_progress"))
    app._lbl_status_section.configure(text=t("section_status"))
    app._lbl_unmoved_section.configure(text=t("section_unmoved"))
    app.export_btn.configure(text=t("btn_export"))

    try:
        done  = app._progress_done
        total = app._progress_total
    except AttributeError:
        done = total = 0
    app.progress_label.configure(text=t("progress_count", done=done, total=total))
