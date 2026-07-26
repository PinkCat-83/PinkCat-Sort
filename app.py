import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

from language.i18n import I18n
from ui.styles import ACCENT, BG_APP, BG_SURFACE, BG_CARD, BG_INPUT
from ui.styles import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
from ui.styles import SUCCESS, ERROR, WARNING, BORDER
from ui.components import build_ui, refresh_ui_texts
from core.sorter import sort_files
from core.report import save_report


class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PinkCat Sort")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_APP)

        self.t = I18n()

        self.path_to_sort = tk.StringVar()
        self.tolerancia = tk.IntVar(value=80)
        self.is_sorting = False
        self.archivos_no_movidos = []   # lista de dicts
        self.log_completo = []
        self.total_archivos = 0
        self.archivos_procesados = 0
        self._progress_done = 0
        self._progress_total = 0
        self._result_movidos = 0
        self._result_ignorados = 0

        build_ui(self)

    # ------------------------------------------------------------------
    # Idioma
    # ------------------------------------------------------------------

    def _on_language_change(self, lang: str):
        self.t.set_language(lang)
        refresh_ui_texts(self)

    # ------------------------------------------------------------------
    # Callbacks de UI
    # ------------------------------------------------------------------

    def update_tolerance_label(self, *args):
        self.tolerance_label.configure(text=f"{self.tolerancia.get()}%")

    def on_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self.path_to_sort.set(path)
            self.log_status(f"✓ {self.t('folder_selected_label')} {path}")
        else:
            messagebox.showwarning(self.t("warning_title"), self.t("error_no_folder"))

    def browse_folder(self):
        folder = filedialog.askdirectory(title=self.t("btn_browse"))
        if folder:
            self.path_to_sort.set(folder)
            self.log_status(f"✓ {self.t('folder_selected_label')} {folder}")

    # ------------------------------------------------------------------
    # Ordenación
    # ------------------------------------------------------------------

    def start_sorting(self):
        if not self.path_to_sort.get():
            messagebox.showwarning(self.t("warning_title"), self.t("error_no_folder"))
            return
        if self.is_sorting:
            return

        self.archivos_no_movidos = []
        self.log_completo = []
        self.total_archivos = 0
        self.archivos_procesados = 0
        self._progress_done = 0
        self._progress_total = 0
        self._result_movidos = 0
        self._result_ignorados = 0

        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")

        self.progress_bar.set(0)
        self.progress_label.configure(text=self.t("progress_count", done=0, total=0))
        self.results_frame.pack_forget()
        try:
            self._lbl_unmoved_section.pack_forget()
        except Exception:
            pass

        self.is_sorting = True
        self.sort_btn.configure(state="disabled", fg_color="#4a4a5a")

        thread = threading.Thread(target=self._run_sorting)
        thread.daemon = True
        thread.start()

    def _run_sorting(self):
        result = sort_files(
            path=self.path_to_sort.get(),
            tolerancia=self.tolerancia.get(),
            on_progress=self._on_progress,
            on_log=self.log_status,
        )
        self.archivos_no_movidos = result["no_movidos"]
        self._result_movidos     = result["movidos"]
        self._result_ignorados   = result["ignorados"]
        self.root.after(0, self._finish_sorting)

    def _on_progress(self, procesados, total):
        self._progress_done = procesados
        self._progress_total = total
        self.archivos_procesados = procesados
        self.total_archivos = total
        self.root.after(0, self._update_progress_bar)

    def _update_progress_bar(self):
        if self.total_archivos > 0:
            frac = self.archivos_procesados / self.total_archivos
            self.progress_bar.set(frac)
            self.progress_label.configure(
                text=self.t("progress_count",
                            done=self.archivos_procesados,
                            total=self.total_archivos)
            )

    def _finish_sorting(self):
        self.sort_btn.configure(state="normal", fg_color=ACCENT)
        self.is_sorting = False
        self._lbl_unmoved_section.pack(anchor=tk.W, pady=(0, 4))
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self._show_unmoved_files()
        self._show_summary_popup()

    # ------------------------------------------------------------------
    # Popup de resumen
    # ------------------------------------------------------------------

    def _show_summary_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("PinkCat Sort — Resumen")
        popup.geometry("620x520")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_SURFACE)
        popup.grab_set()
        popup.focus_set()

        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - 620) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - 520) // 2
        popup.geometry(f"620x520+{rx}+{ry}")

        def f(size, bold=False):
            return ctk.CTkFont(family="Segoe UI", size=size,
                               weight="bold" if bold else "normal")

        # ── Cabecera ──────────────────────────────────────────────────
        header = ctk.CTkFrame(popup, fg_color=BG_CARD, corner_radius=0)
        header.pack(fill=tk.X)

        ctk.CTkLabel(
            header, text="✅  Proceso completado",
            font=f(17, bold=True), text_color=SUCCESS
        ).pack(anchor=tk.W, padx=20, pady=(14, 2))

        ctk.CTkLabel(
            header,
            text=(f"{self._result_movidos} movido(s)  ·  "
                  f"{self._result_ignorados} ignorado(s)  ·  "
                  f"{self.total_archivos} total"),
            font=f(13), text_color=TEXT_SECONDARY
        ).pack(anchor=tk.W, padx=20, pady=(0, 14))

        # ── Cuerpo ────────────────────────────────────────────────────
        body = ctk.CTkFrame(popup, fg_color=BG_SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=14)

        ignorados = [e for e in self.archivos_no_movidos
                     if e["reason"] != "py_file"]
        py_files  = [e for e in self.archivos_no_movidos
                     if e["reason"] == "py_file"]

        if not self.archivos_no_movidos:
            ctk.CTkLabel(
                body,
                text="🎉  ¡Todos los archivos fueron movidos correctamente!",
                font=f(14), text_color=SUCCESS
            ).pack(expand=True)
        else:
            if ignorados:
                ctk.CTkLabel(
                    body,
                    text=f"Archivos no movidos — similitud insuficiente ({len(ignorados)}):",
                    font=f(13, bold=True), text_color=TEXT_PRIMARY
                ).pack(anchor=tk.W, pady=(0, 6))

                table_frame = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=8)
                table_frame.pack(fill=tk.BOTH, expand=True)

                text = tk.Text(
                    table_frame,
                    state="disabled",
                    wrap=tk.NONE,
                    font=("Consolas", 13),
                    bg=BG_CARD,
                    fg=TEXT_PRIMARY,
                    relief=tk.FLAT,
                    borderwidth=0,
                    spacing1=2,
                    spacing3=2,
                )
                # Tags
                text.tag_configure("header_file",   foreground=TEXT_PRIMARY,
                                   font=("Consolas", 13, "bold"))
                text.tag_configure("arrow",         foreground=TEXT_MUTED,
                                   font=("Consolas", 13))
                text.tag_configure("folder",        foreground=TEXT_SECONDARY,
                                   font=("Consolas", 13))
                text.tag_configure("bar_fill_ok",   foreground=WARNING)
                text.tag_configure("bar_fill_low",  foreground=ERROR)
                text.tag_configure("bar_empty",     foreground=TEXT_MUTED)
                text.tag_configure("pct_ok",        foreground=WARNING,
                                   font=("Consolas", 13, "bold"))
                text.tag_configure("pct_low",       foreground=ERROR,
                                   font=("Consolas", 13, "bold"))

                sb_y = ctk.CTkScrollbar(table_frame, command=text.yview,
                                        fg_color=BG_CARD, button_color=BORDER,
                                        button_hover_color=ACCENT)
                sb_x = ctk.CTkScrollbar(table_frame, command=text.xview,
                                        fg_color=BG_CARD, button_color=BORDER,
                                        button_hover_color=ACCENT,
                                        orientation="horizontal")
                sb_y.pack(side=tk.RIGHT, fill=tk.Y)
                sb_x.pack(side=tk.BOTTOM, fill=tk.X)
                text.config(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
                text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

                tolerancia = self.tolerancia.get()
                text.config(state="normal")

                for entry in ignorados:
                    score  = entry["score"]
                    folder = entry["folder"]

                    tag_pct = "pct_ok" if (score is not None and score >= tolerancia * 0.85) else "pct_low"

                    # Nombre del archivo
                    text.insert(tk.END, f"  {entry['file']}\n", "header_file")

                    # Frase comparativa
                    if folder and score is not None:
                        text.insert(tk.END, "  ", "arrow")
                        text.insert(tk.END, f"{score:.1f}%", tag_pct)
                        text.insert(tk.END, " de similitud con ", "arrow")
                        text.insert(tk.END, f"'{folder}'", "folder")
                        text.insert(tk.END, ", que es la mejor carpeta encontrada.\n", "arrow")
                        text.insert(tk.END, f"  (se necesita al menos {tolerancia}%)\n\n", "bar_empty")
                    elif folder:
                        text.insert(tk.END, f"  Mejor carpeta encontrada: '{folder}' — sin puntuación.\n\n", "arrow")
                    else:
                        text.insert(tk.END, "  No se encontraron carpetas disponibles.\n\n", "arrow")

                text.config(state="disabled")

            if py_files:
                ctk.CTkLabel(
                    body,
                    text=f"Archivos .py ignorados ({len(py_files)}): "
                         + ", ".join(e["file"] for e in py_files),
                    font=f(11), text_color=TEXT_MUTED,
                    wraplength=560, justify=tk.LEFT
                ).pack(anchor=tk.W, pady=(8, 0))

        # ── Botón cerrar ──────────────────────────────────────────────
        ctk.CTkButton(
            popup, text="Cerrar",
            command=popup.destroy,
            fg_color=ACCENT,
            hover_color="#c91575",
            text_color="#ffffff",
            font=f(14, bold=True),
            corner_radius=8,
            height=40,
        ).pack(fill=tk.X, padx=20, pady=(0, 16))

    # ------------------------------------------------------------------
    # Log y resultados
    # ------------------------------------------------------------------

    def log_status(self, message):
        self.status_text.config(state="normal")
        line_num = int(self.status_text.index(tk.END).split(".")[0])
        self.status_text.insert(tk.END, message + "\n\n")
        if message.startswith(("⚠️", "❌")):
            self.status_text.tag_add("error",   f"{line_num}.0", f"{line_num}.end")
        elif message.startswith("📦"):
            self.status_text.tag_add("success", f"{line_num}.0", f"{line_num}.end")
        elif message.startswith(("=", "🚀", "✅")):
            self.status_text.tag_add("accent",  f"{line_num}.0", f"{line_num}.end")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.log_completo.append(message)

    def _show_unmoved_files(self):
        self.unmoved_text.config(state="normal")
        self.unmoved_text.delete(1.0, tk.END)
        if not self.archivos_no_movidos:
            self.unmoved_text.insert(
                tk.END, "✓ Todos los archivos fueron procesados correctamente"
            )
            self.unmoved_text.tag_add("success", "1.0", tk.END)
        else:
            for e in self.archivos_no_movidos:
                if e["reason"] == "low_score":
                    self.unmoved_text.insert(
                        tk.END,
                        f"• {e['file']}  →  {e['folder']}  ({e['score']:.1f}%)\n"
                    )
                elif e["reason"] == "py_file":
                    self.unmoved_text.insert(tk.END, f"• {e['file']}  (archivo .py)\n")
                elif e["reason"] == "error":
                    self.unmoved_text.insert(
                        tk.END, f"• {e['file']}  ❌ {e.get('error', '')}\n"
                    )
                else:
                    self.unmoved_text.insert(tk.END, f"• {e['file']}\n")
        self.unmoved_text.config(state="disabled")

    def export_report(self):
        if not self.log_completo:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=f"reporte_ordenacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )
        if file_path:
            try:
                save_report(file_path, self.log_completo, self.archivos_no_movidos)
                messagebox.showinfo("OK", f"Reporte exportado correctamente a:\n{file_path}")
            except Exception as e:
                messagebox.showerror(self.t("error_title"),
                                     f"No se pudo exportar el reporte:\n{str(e)}")
