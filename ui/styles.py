from tkinter import ttk

BG_COLOR = '#f5f5f5'
ACCENT_COLOR = '#4a90e2'
DROP_ZONE_COLOR = '#e8f4f8'
TEXT_COLOR = '#2c3e50'
MUTED_COLOR = '#666'
SUCCESS_COLOR = '#27ae60'
ERROR_COLOR = '#e74c3c'


def apply_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Pink.Horizontal.TProgressbar",
        troughcolor='#e0e0e0',
        background='#ff69b4',
        darkcolor='#ff1493',
        lightcolor='#ffb6c1',
        bordercolor='#c0c0c0'
    )
