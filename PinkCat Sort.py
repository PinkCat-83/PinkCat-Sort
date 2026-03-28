import shutil
import os
import unicodedata
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from rapidfuzz import process, fuzz
import threading
from datetime import datetime

class FileSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordenador de Archivos")
        self.root.geometry("700x750")
        self.root.resizable(True, True)
        self.root.minsize(600, 600)
        
        # Variables
        self.path_to_sort = tk.StringVar()
        self.tolerancia = tk.IntVar(value=80)
        self.is_sorting = False
        self.archivos_no_movidos = []
        self.log_completo = []
        self.total_archivos = 0
        self.archivos_procesados = 0
        
        # Configurar el estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        self.bg_color = '#f5f5f5'
        self.accent_color = '#4a90e2'
        self.drop_zone_color = '#e8f4f8'
        
        self.root.configure(bg=self.bg_color)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal con padding y color de fondo
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=25, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="📁 Ordenador de Archivos", 
                              font=('Segoe UI', 20, 'bold'),
                              bg=self.bg_color, fg='#2c3e50')
        title_label.pack(pady=(0, 25))
        
        # Zona de arrastrar y soltar
        drop_frame = tk.Frame(main_frame, bg=self.drop_zone_color, relief=tk.SOLID, 
                             borderwidth=2, height=110)
        drop_frame.pack(fill=tk.X, pady=(0, 15))
        drop_frame.pack_propagate(False)
        
        # Registrar el drop target
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        drop_label = tk.Label(drop_frame, text="🗂️\n\nArrastra aquí la carpeta a ordenar\no haz clic en 'Examinar'",
                             bg=self.drop_zone_color, font=('Segoe UI', 11), fg='#555')
        drop_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Path seleccionado
        path_label = tk.Label(main_frame, text="Carpeta seleccionada:", 
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.bg_color, fg='#2c3e50')
        path_label.pack(anchor=tk.W, pady=(0, 5))
        
        path_entry = ttk.Entry(main_frame, textvariable=self.path_to_sort, 
                              state='readonly', width=60, font=('Segoe UI', 9))
        path_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Botón examinar
        browse_btn = tk.Button(main_frame, text="📂 Examinar", 
                              command=self.browse_folder,
                              bg='white', fg='#2c3e50',
                              font=('Segoe UI', 10),
                              relief=tk.SOLID, borderwidth=1,
                              padx=20, pady=8,
                              cursor='hand2')
        browse_btn.pack(pady=(0, 20))
        
        # Frame de configuración con mejor diseño
        config_frame = tk.LabelFrame(main_frame, text=" ⚙️ Configuración ", 
                                    bg=self.bg_color, fg='#2c3e50',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief=tk.SOLID, borderwidth=1,
                                    padx=15, pady=15)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título de tolerancia
        tolerance_title = tk.Label(config_frame, 
                                  text="Tolerancia de similitud:", 
                                  bg=self.bg_color, fg='#2c3e50',
                                  font=('Segoe UI', 10, 'bold'))
        tolerance_title.pack(anchor=tk.W)
        
        # Explicación de tolerancia
        tolerance_info = tk.Label(config_frame, 
                                 text="Define qué tan similares deben ser los nombres para mover archivos.\n"
                                      "Mayor valor = mayor precisión requerida (80-90 recomendado)",
                                 bg=self.bg_color, fg='#666',
                                 font=('Segoe UI', 9),
                                 justify=tk.LEFT)
        tolerance_info.pack(anchor=tk.W, pady=(3, 10))
        
        # Frame para el slider y el valor
        slider_frame = tk.Frame(config_frame, bg=self.bg_color)
        slider_frame.pack(fill=tk.X)
        
        tolerance_scale = ttk.Scale(slider_frame, from_=0, to=100, 
                                   variable=self.tolerancia, orient=tk.HORIZONTAL)
        tolerance_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.tolerance_label = tk.Label(slider_frame, text="80%", 
                                       font=('Segoe UI', 11, 'bold'),
                                       bg=self.bg_color, fg=self.accent_color,
                                       width=5)
        self.tolerance_label.pack(side=tk.RIGHT)
        
        # Actualizar label cuando cambia el slider
        self.tolerancia.trace_add('write', self.update_tolerance_label)
        
        # Botón ordenar (más grande y destacado)
        self.sort_btn = tk.Button(main_frame, text="🚀 Ordenar Archivos", 
                                 command=self.start_sorting,
                                 bg=self.accent_color, fg='white',
                                 font=('Segoe UI', 12, 'bold'),
                                 relief=tk.FLAT,
                                 padx=30, pady=12,
                                 cursor='hand2')
        self.sort_btn.pack(pady=(0, 20))
        
        # Efectos hover para el botón
        self.sort_btn.bind('<Enter>', lambda e: self.sort_btn.config(bg='#357abd'))
        self.sort_btn.bind('<Leave>', lambda e: self.sort_btn.config(bg=self.accent_color))
        
        # Barra de progreso rosa (determinada)
        progress_label = tk.Label(main_frame, text="Progreso:", 
                                 bg=self.bg_color, fg='#2c3e50',
                                 font=('Segoe UI', 9, 'bold'))
        progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        style = ttk.Style()
        style.configure("Pink.Horizontal.TProgressbar", 
                       troughcolor='#e0e0e0',
                       background='#ff69b4',
                       darkcolor='#ff1493',
                       lightcolor='#ffb6c1',
                       bordercolor='#c0c0c0')
        
        self.progress_bar = ttk.Progressbar(main_frame, 
                                           mode='determinate',
                                           style="Pink.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Label de progreso
        self.progress_label = tk.Label(main_frame, text="0 / 0 archivos procesados", 
                                      bg=self.bg_color, fg='#666',
                                      font=('Segoe UI', 9))
        self.progress_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Frame de estado en tiempo real
        status_frame = tk.LabelFrame(main_frame, text=" 📊 Estado del proceso ", 
                                    bg=self.bg_color, fg='#2c3e50',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief=tk.SOLID, borderwidth=1,
                                    padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Área de estado actual
        self.status_text = tk.Text(status_frame, height=8, 
                                  state='disabled', wrap=tk.WORD, 
                                  font=('Consolas', 9),
                                  bg='#ffffff', fg='#2c3e50',
                                  relief=tk.FLAT, borderwidth=0)
        self.status_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, 
                                        command=self.status_text.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=status_scrollbar.set)
        
        # Barra de progreso indeterminada (oculta por defecto)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        # No la empaquetamos aquí, solo cuando sea necesaria
        
        # Frame de resultados (inicialmente oculto)
        self.results_frame = tk.LabelFrame(main_frame, text=" 📋 Archivos no movidos ", 
                                          bg=self.bg_color, fg='#2c3e50',
                                          font=('Segoe UI', 10, 'bold'),
                                          relief=tk.SOLID, borderwidth=1,
                                          padx=10, pady=10)
        
        # Lista de archivos no movidos
        list_frame = tk.Frame(self.results_frame, bg='#ffffff')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.unmoved_text = tk.Text(list_frame, height=6, 
                                   state='disabled', wrap=tk.WORD, 
                                   font=('Consolas', 9),
                                   bg='#ffffff', fg='#e74c3c',
                                   relief=tk.FLAT, borderwidth=0)
        self.unmoved_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        unmoved_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                         command=self.unmoved_text.yview)
        unmoved_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.unmoved_text.config(yscrollcommand=unmoved_scrollbar.set)
        
        # Botón exportar
        self.export_btn = tk.Button(self.results_frame, text="💾 Exportar Reporte a TXT", 
                                   command=self.export_report,
                                   bg='#27ae60', fg='white',
                                   font=('Segoe UI', 10, 'bold'),
                                   relief=tk.FLAT,
                                   padx=20, pady=8,
                                   cursor='hand2')
        self.export_btn.pack(pady=(10, 0))
        
        # Efectos hover para el botón exportar
        self.export_btn.bind('<Enter>', lambda e: self.export_btn.config(bg='#229954'))
        self.export_btn.bind('<Leave>', lambda e: self.export_btn.config(bg='#27ae60'))
        
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
            
    def log_status(self, message):
        """Registra mensajes en el área de estado en tiempo real"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + '\n')
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.log_completo.append(message)
        
    def show_unmoved_files(self):
        """Muestra los archivos que no se movieron"""
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
        """Exporta el reporte completo a un archivo TXT"""
        if not self.log_completo:
            messagebox.showinfo("Info", "No hay información para exportar")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=f"reporte_ordenacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 70 + "\n")
                    f.write("REPORTE DE ORDENACIÓN DE ARCHIVOS\n")
                    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 70 + "\n\n")
                    
                    f.write("PROCESO COMPLETO:\n")
                    f.write("-" * 70 + "\n")
                    for line in self.log_completo:
                        f.write(line + "\n")
                    
                    if self.archivos_no_movidos:
                        f.write("\n" + "=" * 70 + "\n")
                        f.write("ARCHIVOS NO MOVIDOS:\n")
                        f.write("=" * 70 + "\n")
                        for archivo in self.archivos_no_movidos:
                            f.write(f"• {archivo}\n")
                
                messagebox.showinfo("Éxito", f"Reporte exportado correctamente a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar el reporte:\n{str(e)}")
        
    def start_sorting(self):
        if not self.path_to_sort.get():
            messagebox.showwarning("Aviso", "Por favor, selecciona una carpeta primero")
            return
            
        if self.is_sorting:
            messagebox.showinfo("Info", "Ya hay un proceso de ordenación en curso")
            return
        
        # Limpiar estado previo
        self.archivos_no_movidos = []
        self.log_completo = []
        self.total_archivos = 0
        self.archivos_procesados = 0
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')
        
        # Resetear barra de progreso
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0 / 0 archivos procesados")
        
        # Ocultar frame de resultados
        self.results_frame.pack_forget()
        
        # Ejecutar en un hilo separado
        self.is_sorting = True
        self.sort_btn.config(state='disabled', bg='#95a5a6')
        
        thread = threading.Thread(target=self.sort_files)
        thread.daemon = True
        thread.start()
        
    def update_progress(self):
        """Actualiza la barra de progreso rosa"""
        if self.total_archivos > 0:
            progress_percent = (self.archivos_procesados / self.total_archivos) * 100
            self.progress_bar['value'] = progress_percent
            self.progress_label.config(
                text=f"{self.archivos_procesados} / {self.total_archivos} archivos procesados"
            )
    
    def sort_files(self):
        path = self.path_to_sort.get()
        tolerancia = self.tolerancia.get()
        
        self.log_status("\n" + "=" * 50)
        self.log_status("🚀 INICIANDO PROCESO DE ORDENACIÓN")
        self.log_status("=" * 50)
        
        file_names = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        
        self.total_archivos = len(file_names)
        self.archivos_procesados = 0
        
        self.log_status(f"📊 Total de archivos encontrados: {self.total_archivos}")
        self.log_status(f"⚙️ Tolerancia configurada: {tolerancia}%\n")
        
        # Actualizar UI con el total
        self.root.after(0, self.update_progress)
        
        archivos_movidos = 0
        archivos_ignorados = 0
        
        for file_name in file_names:
            origen = os.path.join(path, file_name)
            
            try:
                if not file_name.endswith(".py"):
                    folder_name = self.look_closer_folder_name(file_name, path)
                    score = fuzz.ratio(self.normalize_text(file_name), 
                                      self.normalize_text(folder_name))
                    
                    if folder_name != "ERROR" and score >= tolerancia:
                        self.log_status(f"📦 Moviendo '{file_name}' → '{folder_name}' (similitud: {score}%)")
                        destino = os.path.join(path, folder_name)
                        shutil.move(origen, os.path.join(destino, file_name))
                        archivos_movidos += 1
                        self.archivos_procesados += 1
                        self.root.after(0, self.update_progress)
                    else:
                        self.log_status(f"⚠️ Sin destino para '{file_name}' (similitud: {score}%)")
                        self.archivos_no_movidos.append(f"{file_name} (similitud: {score}%)")
                        archivos_ignorados += 1
                        self.archivos_procesados += 1
                        self.root.after(0, self.update_progress)
                else:
                    self.archivos_no_movidos.append(f"{file_name} (archivo .py - ignorado)")
                    archivos_ignorados += 1
                    self.archivos_procesados += 1
                    self.root.after(0, self.update_progress)
                    
            except Exception as e:
                error_msg = f"{file_name}: {str(e)}"
                self.archivos_no_movidos.append(error_msg)
                self.log_status(f"❌ Error con '{file_name}': {str(e)}")
                self.archivos_procesados += 1
                self.root.after(0, self.update_progress)
                
        self.log_status("\n" + "=" * 50)
        self.log_status("✅ PROCESO COMPLETADO")
        self.log_status("=" * 50)
        self.log_status(f"📈 Archivos movidos: {archivos_movidos}")
        self.log_status(f"⭐ Archivos ignorados: {archivos_ignorados}")
        
        self.root.after(0, self.finish_sorting)
        
    def finish_sorting(self):
        self.sort_btn.config(state='normal', bg=self.accent_color)
        self.is_sorting = False
        
        # Mostrar frame de resultados
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self.show_unmoved_files()
        
        messagebox.showinfo("Completado", "¡Proceso de ordenación finalizado!")
        
    def look_closer_folder_name(self, file_name, path):
        folder_names = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        
        try:
            normalized_file = self.normalize_text(file_name)
            folder_name, score, _ = process.extractOne(normalized_file, folder_names, 
                                                       scorer=fuzz.ratio)
            return folder_name
        except Exception:
            return "ERROR"
            
    def normalize_text(self, text):
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

def main():
    root = TkinterDnD.Tk()
    app = FileSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()