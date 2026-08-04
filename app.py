import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk
from PIL import Image
from tkinterdnd2 import TkinterDnD

from core.config import load_config, save_config
from language.i18n import I18n
from ui.styles import ACCENT, ACCENT_DIM, BG_APP, BG_SURFACE, BG_CARD, BG_INPUT
from ui.styles import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
from ui.styles import SUCCESS, ERROR, WARNING, BORDER
from ui.styles import FONT_FAMILY_UI, FONT_FAMILY_MONO
from ui.components import build_ui, refresh_ui_texts
from core.sorter import sort_files
from core.report import save_report

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_ROOT, "ico", "PinkCat-Sort.ico")
LOGO_PATH = os.path.join(APP_ROOT, "ico", "PinkCat-Logo.png")

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
LOGO_HEIGHT = 48

SUMMARY_WINDOW_WIDTH = 620
SUMMARY_WINDOW_HEIGHT = 520


class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.config = load_config()

        self.t = I18n(self.config["language"])

        self.root.title(self.t("app_title"))
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_APP)
        _set_window_icon(self.root)

        self.logo_image = _load_logo_image()

        self.path_to_sort = tk.StringVar()
        self.tolerance = tk.IntVar(value=80)
        self.is_sorting = False
        self.unmoved_files = []   # list of dicts
        self.full_log = []
        self.total_files = 0
        self.processed_files = 0
        self._progress_done = 0
        self._progress_total = 0
        self._result_moved = 0
        self._result_ignored = 0

        build_ui(self)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _on_language_change(self, lang: str):
        self.t.set_language(lang)
        self.config["language"] = lang
        save_config(self.config)
        refresh_ui_texts(self)

    def _on_theme_change(self, theme_name: str):
        self.config["theme"] = theme_name
        save_config(self.config)
        messagebox.showinfo(self.t("info_title"), self.t("theme_restart_notice"))

    # ------------------------------------------------------------------
    # UI callbacks
    # ------------------------------------------------------------------

    def update_tolerance_label(self, *args):
        self.tolerance_label.configure(text=f"{self.tolerance.get()}%")

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
    # Sorting
    # ------------------------------------------------------------------

    def start_sorting(self):
        if not self.path_to_sort.get():
            messagebox.showwarning(self.t("warning_title"), self.t("error_no_folder"))
            return
        if self.is_sorting:
            return

        self.unmoved_files = []
        self.full_log = []
        self.total_files = 0
        self.processed_files = 0
        self._progress_done = 0
        self._progress_total = 0
        self._result_moved = 0
        self._result_ignored = 0

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
        self.sort_btn.configure(state="disabled", fg_color=BORDER, text_color=TEXT_MUTED)

        thread = threading.Thread(target=self._run_sorting)
        thread.daemon = True
        thread.start()

    def _run_sorting(self):
        result = sort_files(
            path=self.path_to_sort.get(),
            tolerance=self.tolerance.get(),
            on_progress=self._on_progress,
            on_log=self.log_status,
            t=self.t,
        )
        self.unmoved_files = result["unmoved"]
        self._result_moved   = result["moved"]
        self._result_ignored = result["ignored"]
        self.root.after(0, self._finish_sorting)

    def _on_progress(self, processed, total):
        self._progress_done = processed
        self._progress_total = total
        self.processed_files = processed
        self.total_files = total
        self.root.after(0, self._update_progress_bar)

    def _update_progress_bar(self):
        if self.total_files > 0:
            frac = self.processed_files / self.total_files
            self.progress_bar.set(frac)
            self.progress_label.configure(
                text=self.t("progress_count",
                            done=self.processed_files,
                            total=self.total_files)
            )

    def _finish_sorting(self):
        self.sort_btn.configure(state="normal", fg_color=ACCENT_DIM, text_color="#ffffff")
        self.is_sorting = False
        self._lbl_unmoved_section.pack(anchor=tk.W, pady=(0, 4))
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self._show_unmoved_files()
        self._show_summary_popup()

    # ------------------------------------------------------------------
    # Summary popup
    # ------------------------------------------------------------------

    def _show_summary_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title(self.t("summary_window_title"))
        popup.geometry(f"{SUMMARY_WINDOW_WIDTH}x{SUMMARY_WINDOW_HEIGHT}")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_SURFACE)
        _set_window_icon(popup)
        popup.grab_set()
        popup.focus_set()

        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - SUMMARY_WINDOW_WIDTH) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - SUMMARY_WINDOW_HEIGHT) // 2
        popup.geometry(f"{SUMMARY_WINDOW_WIDTH}x{SUMMARY_WINDOW_HEIGHT}+{rx}+{ry}")

        def f(size, bold=False):
            return ctk.CTkFont(family=FONT_FAMILY_UI, size=size,
                               weight="bold" if bold else "normal")

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(popup, fg_color=BG_CARD, corner_radius=0)
        header.pack(fill=tk.X)

        ctk.CTkLabel(
            header, text=self.t("summary_completed_header"),
            font=f(17, bold=True), text_color=SUCCESS
        ).pack(anchor=tk.W, padx=20, pady=(14, 2))

        ctk.CTkLabel(
            header,
            text=self.t("summary_stats",
                        moved=self._result_moved,
                        ignored=self._result_ignored,
                        total=self.total_files),
            font=f(13), text_color=TEXT_SECONDARY
        ).pack(anchor=tk.W, padx=20, pady=(0, 14))

        # ── Body ──────────────────────────────────────────────────────
        body = ctk.CTkFrame(popup, fg_color=BG_SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=14)

        unmatched = [e for e in self.unmoved_files if e["reason"] != "py_file"]
        py_files  = [e for e in self.unmoved_files if e["reason"] == "py_file"]

        if not self.unmoved_files:
            ctk.CTkLabel(
                body,
                text=self.t("summary_all_moved"),
                font=f(14), text_color=SUCCESS
            ).pack(expand=True)
        else:
            if unmatched:
                ctk.CTkLabel(
                    body,
                    text=self.t("summary_unmoved_header", count=len(unmatched)),
                    font=f(13, bold=True), text_color=TEXT_PRIMARY
                ).pack(anchor=tk.W, pady=(0, 6))

                table_frame = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=8)
                table_frame.pack(fill=tk.BOTH, expand=True)

                text = tk.Text(
                    table_frame,
                    state="disabled",
                    wrap=tk.NONE,
                    font=(FONT_FAMILY_MONO, 13),
                    bg=BG_CARD,
                    fg=TEXT_PRIMARY,
                    relief=tk.FLAT,
                    borderwidth=0,
                    spacing1=2,
                    spacing3=2,
                )
                # Tags
                text.tag_configure("header_file",   foreground=TEXT_PRIMARY,
                                   font=(FONT_FAMILY_MONO, 13, "bold"))
                text.tag_configure("line_ok",       foreground=WARNING)
                text.tag_configure("line_low",      foreground=ERROR)
                text.tag_configure("bar_empty",     foreground=TEXT_MUTED)

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

                tolerance = self.tolerance.get()
                text.config(state="normal")

                for entry in unmatched:
                    score  = entry["score"]
                    folder = entry["folder"]

                    text.insert(tk.END, f"  {entry['file']}\n", "header_file")

                    if folder and score is not None:
                        line_tag = "line_ok" if score >= tolerance * 0.85 else "line_low"
                        text.insert(
                            tk.END,
                            "  " + self.t("summary_similarity_line", score=f"{score:.1f}%", folder=folder) + "\n",
                            line_tag,
                        )
                        text.insert(
                            tk.END,
                            "  " + self.t("summary_min_required", tolerance=tolerance) + "\n\n",
                            "bar_empty",
                        )
                    elif folder:
                        text.insert(tk.END, "  " + self.t("summary_folder_no_score", folder=folder) + "\n\n", "bar_empty")
                    else:
                        text.insert(tk.END, "  " + self.t("summary_no_folders") + "\n\n", "bar_empty")

                text.config(state="disabled")

            if py_files:
                ctk.CTkLabel(
                    body,
                    text=self.t("summary_py_ignored",
                                count=len(py_files),
                                list=", ".join(e["file"] for e in py_files)),
                    font=f(11), text_color=TEXT_MUTED,
                    wraplength=560, justify=tk.LEFT
                ).pack(anchor=tk.W, pady=(8, 0))

        # ── Close button ─────────────────────────────────────────────
        ctk.CTkButton(
            popup, text=self.t("btn_close"),
            command=popup.destroy,
            fg_color=ACCENT_DIM,
            hover_color=ACCENT,
            text_color="#ffffff",
            font=f(14, bold=True),
            corner_radius=8,
            height=40,
        ).pack(fill=tk.X, padx=20, pady=(0, 16))

    # ------------------------------------------------------------------
    # Log and results
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
        self.full_log.append(message)

    def _show_unmoved_files(self):
        self.unmoved_text.config(state="normal")
        self.unmoved_text.delete(1.0, tk.END)
        if not self.unmoved_files:
            self.unmoved_text.insert(tk.END, self.t("unmoved_all_ok"))
            self.unmoved_text.tag_add("success", "1.0", tk.END)
        else:
            for e in self.unmoved_files:
                if e["reason"] == "low_score":
                    self.unmoved_text.insert(
                        tk.END,
                        f"• {e['file']}  →  {e['folder']}  ({e['score']:.1f}%)\n"
                    )
                elif e["reason"] == "py_file":
                    self.unmoved_text.insert(tk.END, f"• {e['file']}  ({self.t('unmoved_py_file')})\n")
                elif e["reason"] == "error":
                    self.unmoved_text.insert(
                        tk.END, f"• {e['file']}  ❌ {e.get('error', '')}\n"
                    )
                else:
                    self.unmoved_text.insert(tk.END, f"• {e['file']}\n")
        self.unmoved_text.config(state="disabled")

    def export_report(self):
        if not self.full_log:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"sort_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )
        if file_path:
            try:
                save_report(file_path, self.full_log, self.unmoved_files, self.t)
                messagebox.showinfo(self.t("info_title"), self.t("export_success_msg", path=file_path))
            except Exception as e:
                messagebox.showerror(self.t("error_title"),
                                     self.t("export_error_msg", error=str(e)))


# ------------------------------------------------------------------
# Window chrome helpers
# ------------------------------------------------------------------

def _set_window_icon(window) -> None:
    if os.path.isfile(ICON_PATH):
        try:
            window.iconbitmap(ICON_PATH)
        except tk.TclError:
            pass


def _load_logo_image():
    if not os.path.isfile(LOGO_PATH):
        return None
    image = Image.open(LOGO_PATH)
    width = int(LOGO_HEIGHT * (image.width / image.height))
    return ctk.CTkImage(light_image=image, dark_image=image, size=(width, LOGO_HEIGHT))
