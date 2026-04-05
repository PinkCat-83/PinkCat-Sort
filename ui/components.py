import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES
from ui.styles import (
    BG_COLOR, ACCENT_COLOR, DROP_ZONE_COLOR,
    TEXT_COLOR, MUTED_COLOR, SUCCESS_COLOR, ERROR_COLOR
)


def build_ui(app):
    """Construye todos los widgets de la interfaz y los asocia a `app`."""
    root = app.root
    root.configure(bg=BG_COLOR)

    main_frame = tk.Frame(root, bg=BG_COLOR, padx=25, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    tk.Label(
        main_frame, text="📁 PinkCat Sort - Ordena tus archivos rápidamente",
        font=('Segoe UI', 20, 'bold'),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=(0, 25))

    # ── Contenedor de dos columnas ──────────────────────────────────────────
    columns_frame = tk.Frame(main_frame, bg=BG_COLOR)
    columns_frame.pack(fill=tk.BOTH, expand=True)

    columns_frame.columnconfigure(0, weight=2)
    columns_frame.columnconfigure(1, weight=3)
    columns_frame.rowconfigure(0, weight=1)

    # ── COLUMNA IZQUIERDA: configuración ────────────────────────────────────
    left_frame = tk.Frame(columns_frame, bg=BG_COLOR, padx=(0), pady=0)
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 12))

    # Zona de arrastrar y soltar
    drop_frame = tk.Frame(
        left_frame, bg=DROP_ZONE_COLOR,
        relief=tk.SOLID, borderwidth=2, height=110
    )
    drop_frame.pack(fill=tk.X, pady=(0, 15))
    drop_frame.pack_propagate(False)
    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind('<<Drop>>', app.on_drop)

    tk.Label(
        drop_frame,
        text="🗂️\n\nArrastra aquí la carpeta a ordenar\no haz clic en 'Examinar'",
        bg=DROP_ZONE_COLOR, font=('Segoe UI', 11), fg=MUTED_COLOR
    ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Carpeta seleccionada
    tk.Label(
        left_frame, text="Carpeta seleccionada:",
        font=('Segoe UI', 10, 'bold'),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(anchor=tk.W, pady=(0, 5))

    ttk.Entry(
        left_frame, textvariable=app.path_to_sort,
        state='readonly', font=('Segoe UI', 9)
    ).pack(fill=tk.X, pady=(0, 15))

    # Botón examinar
    tk.Button(
        left_frame, text="📂 Examinar",
        command=app.browse_folder,
        bg='white', fg=TEXT_COLOR,
        font=('Segoe UI', 10),
        relief=tk.SOLID, borderwidth=1,
        padx=20, pady=8, cursor='hand2'
    ).pack(pady=(0, 20))

    # Configuración de tolerancia
    config_frame = tk.LabelFrame(
        left_frame, text=" ⚙️ Configuración ",
        bg=BG_COLOR, fg=TEXT_COLOR,
        font=('Segoe UI', 10, 'bold'),
        relief=tk.SOLID, borderwidth=1,
        padx=15, pady=15
    )
    config_frame.pack(fill=tk.X, pady=(0, 20))

    tk.Label(
        config_frame, text="Tolerancia de similitud:",
        bg=BG_COLOR, fg=TEXT_COLOR,
        font=('Segoe UI', 10, 'bold')
    ).pack(anchor=tk.W)

    tk.Label(
        config_frame,
        text=(
            "Define qué tan similares deben ser los nombres para mover archivos.\n"
            "Mayor valor = mayor precisión requerida (80-90 recomendado)"
        ),
        bg=BG_COLOR, fg=MUTED_COLOR,
        font=('Segoe UI', 9), justify=tk.LEFT
    ).pack(anchor=tk.W, pady=(3, 10))

    slider_frame = tk.Frame(config_frame, bg=BG_COLOR)
    slider_frame.pack(fill=tk.X)

    ttk.Scale(
        slider_frame, from_=0, to=100,
        variable=app.tolerancia, orient=tk.HORIZONTAL
    ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    app.tolerance_label = tk.Label(
        slider_frame, text="80%",
        font=('Segoe UI', 11, 'bold'),
        bg=BG_COLOR, fg=ACCENT_COLOR, width=5
    )
    app.tolerance_label.pack(side=tk.RIGHT)
    app.tolerancia.trace_add('write', app.update_tolerance_label)

    # Botón ordenar
    app.sort_btn = tk.Button(
        left_frame, text="🚀 Ordenar Archivos",
        command=app.start_sorting,
        bg=ACCENT_COLOR, fg='white',
        font=('Segoe UI', 12, 'bold'),
        relief=tk.FLAT, padx=30, pady=12, cursor='hand2'
    )
    app.sort_btn.pack(pady=(0, 20))
    app.sort_btn.bind('<Enter>', lambda e: app.sort_btn.config(bg='#357abd'))
    app.sort_btn.bind('<Leave>', lambda e: app.sort_btn.config(bg=ACCENT_COLOR))

    # ── COLUMNA DERECHA: progreso y resultados ──────────────────────────────
    right_frame = tk.Frame(columns_frame, bg=BG_COLOR, pady=0)
    right_frame.grid(row=0, column=1, sticky='nsew', padx=(12, 0))
    right_frame.rowconfigure(1, weight=1)   # estado del proceso se expande
    right_frame.rowconfigure(2, weight=1)   # archivos no movidos también

    # Barra de progreso
    tk.Label(
        right_frame, text="Progreso:",
        bg=BG_COLOR, fg=TEXT_COLOR,
        font=('Segoe UI', 9, 'bold')
    ).pack(anchor=tk.W, pady=(0, 5))

    app.progress_bar = ttk.Progressbar(
        right_frame, mode='determinate',
        style="Pink.Horizontal.TProgressbar"
    )
    app.progress_bar.pack(fill=tk.X, pady=(0, 5))

    app.progress_label = tk.Label(
        right_frame, text="0 / 0 archivos procesados",
        bg=BG_COLOR, fg=MUTED_COLOR, font=('Segoe UI', 9)
    )
    app.progress_label.pack(anchor=tk.W, pady=(0, 15))

    # Panel de estado
    status_frame = tk.LabelFrame(
        right_frame, text=" 📊 Estado del proceso ",
        bg=BG_COLOR, fg=TEXT_COLOR,
        font=('Segoe UI', 10, 'bold'),
        relief=tk.SOLID, borderwidth=1,
        padx=10, pady=10
    )
    status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    app.status_text = tk.Text(
        status_frame, height=8,
        state='disabled', wrap=tk.WORD,
        font=('Consolas', 9),
        bg='#ffffff', fg=TEXT_COLOR,
        relief=tk.FLAT, borderwidth=0,
        spacing3=6
    )
    app.status_text.tag_configure('error', foreground=ERROR_COLOR)
    app.status_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=app.status_text.yview)
    status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.status_text.config(yscrollcommand=status_scrollbar.set)

    # Frame de archivos no movidos (oculto inicialmente)
    app.results_frame = tk.LabelFrame(
        right_frame, text=" 📋 Archivos no movidos ",
        bg=BG_COLOR, fg=TEXT_COLOR,
        font=('Segoe UI', 10, 'bold'),
        relief=tk.SOLID, borderwidth=1,
        padx=10, pady=10
    )

    list_frame = tk.Frame(app.results_frame, bg='#ffffff')
    list_frame.pack(fill=tk.BOTH, expand=True)

    app.unmoved_text = tk.Text(
        list_frame, height=6,
        state='disabled', wrap=tk.WORD,
        font=('Consolas', 9),
        bg='#ffffff', fg=ERROR_COLOR,
        relief=tk.FLAT, borderwidth=0
    )
    app.unmoved_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    unmoved_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=app.unmoved_text.yview)
    unmoved_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.unmoved_text.config(yscrollcommand=unmoved_scrollbar.set)

    app.export_btn = tk.Button(
        app.results_frame, text="💾 Exportar Reporte a TXT",
        command=app.export_report,
        bg=SUCCESS_COLOR, fg='white',
        font=('Segoe UI', 10, 'bold'),
        relief=tk.FLAT, padx=20, pady=8, cursor='hand2'
    )
    app.export_btn.pack(pady=(10, 0))
    app.export_btn.bind('<Enter>', lambda e: app.export_btn.config(bg='#229954'))
    app.export_btn.bind('<Leave>', lambda e: app.export_btn.config(bg=SUCCESS_COLOR))
