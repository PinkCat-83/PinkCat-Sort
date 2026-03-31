import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from ui.styles import apply_styles, ACCENT_COLOR
from ui.components import build_ui
from core.sorter import sort_files
from core.report import save_report


class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordenador de Archivos")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        # Estado
        self.path_to_sort = tk.StringVar()
        self.tolerancia = tk.IntVar(value=80)
        self.is_sorting = False
        self.archivos_no_movidos = []
        self.log_completo = []
        self.total_archivos = 0
        self.archivos_procesados = 0

        apply_styles()
        build_ui(self)

    # ------------------------------------------------------------------
    # Callbacks de UI
    # ------------------------------------------------------------------

    def update_tolerance_label(self, *args):
        self.tolerance_label.config(text=f"{self.tolerancia.get()}%")

    def on_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self.path_to_sort.set(path)
            self.log_status(f"✓ Carpeta seleccionada: {path}")
        else:
            messagebox.showwarning("Aviso", "Por favor, arrastra una carpeta válida")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Selecciona la carpeta a ordenar")
        if folder:
            self.path_to_sort.set(folder)
            self.log_status(f"✓ Carpeta seleccionada: {folder}")

    # ------------------------------------------------------------------
    # Ordenación
    # ------------------------------------------------------------------

    def start_sorting(self):
        if not self.path_to_sort.get():
            messagebox.showwarning("Aviso", "Por favor, selecciona una carpeta primero")
            return
        if self.is_sorting:
            messagebox.showinfo("Info", "Ya hay un proceso de ordenación en curso")
            return

        self.archivos_no_movidos = []
        self.log_completo = []
        self.total_archivos = 0
        self.archivos_procesados = 0

        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')

        self.progress_bar['value'] = 0
        self.progress_label.config(text="0 / 0 archivos procesados")
        self.results_frame.pack_forget()

        self.is_sorting = True
        self.sort_btn.config(state='disabled', bg='#95a5a6')

        thread = threading.Thread(target=self._run_sorting)
        thread.daemon = True
        thread.start()

    def _run_sorting(self):
        result = sort_files(
            path=self.path_to_sort.get(),
            tolerancia=self.tolerancia.get(),
            on_progress=self._on_progress,
            on_log=self.log_status
        )
        self.archivos_no_movidos = result["no_movidos"]
        self.root.after(0, self._finish_sorting)

    def _on_progress(self, procesados, total):
        self.archivos_procesados = procesados
        self.total_archivos = total
        self.root.after(0, self._update_progress_bar)

    def _update_progress_bar(self):
        if self.total_archivos > 0:
            pct = (self.archivos_procesados / self.total_archivos) * 100
            self.progress_bar['value'] = pct
            self.progress_label.config(
                text=f"{self.archivos_procesados} / {self.total_archivos} archivos procesados"
            )

    def _finish_sorting(self):
        self.sort_btn.config(state='normal', bg=ACCENT_COLOR)
        self.is_sorting = False
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self._show_unmoved_files()
        messagebox.showinfo("Completado", "¡Proceso de ordenación finalizado!")

    # ------------------------------------------------------------------
    # Log y resultados
    # ------------------------------------------------------------------

    def log_status(self, message):
        self.status_text.config(state='normal')
        is_error = message.startswith(('⚠️', '❌'))
        line_num = int(self.status_text.index(tk.END).split('.')[0])
        self.status_text.insert(tk.END, message + '\n\n')
        if is_error:
            self.status_text.tag_add('error', f'{line_num}.0', f'{line_num}.end')
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.log_completo.append(message)

    def _show_unmoved_files(self):
        self.unmoved_text.config(state='normal')
        self.unmoved_text.delete(1.0, tk.END)
        if not self.archivos_no_movidos:
            self.unmoved_text.insert(tk.END, "✓ Todos los archivos fueron procesados correctamente")
            self.unmoved_text.tag_add("success", "1.0", tk.END)
            self.unmoved_text.tag_config("success", foreground='#27ae60')
        else:
            for archivo in self.archivos_no_movidos:
                self.unmoved_text.insert(tk.END, f"• {archivo}\n")
        self.unmoved_text.config(state='disabled')

    def export_report(self):
        if not self.log_completo:
            messagebox.showinfo("Info", "No hay información para exportar")
            return

        from datetime import datetime
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=f"reporte_ordenacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if file_path:
            try:
                save_report(file_path, self.log_completo, self.archivos_no_movidos)
                messagebox.showinfo("Éxito", f"Reporte exportado correctamente a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar el reporte:\n{str(e)}")
