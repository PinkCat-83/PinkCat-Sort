# 🐱🌸 PinkCat Sort

**PinkCat Sort** es una aplicación de escritorio que organiza automáticamente archivos en carpetas usando coincidencia aproximada de nombres. Selecciona una carpeta, ajusta la tolerancia y deja que PinkCat Sort haga el resto.

---

## ✨ Características

- 🗂️ **Arrastrar y soltar** — arrastra una carpeta directamente a la ventana
- 🔍 **Coincidencia aproximada** — empareja archivos con carpetas aunque los nombres tengan pequeñas diferencias
- ⚙️ **Tolerancia configurable** — ajusta el umbral de similitud (0–100%) para controlar la precisión
- 📊 **Progreso en tiempo real** — barra de progreso y registro de estado durante la ordenación
- 💾 **Exportar informe** — guarda el log completo como `.txt`
- 🚫 **Los archivos `.py` se ignoran automáticamente**

---

## 🖥️ Requisitos

- Python 3.8+
- `tkinterdnd2`
- `rapidfuzz`

---

## 🚀 Uso

```bash
python Ordenar.py
```

1. Selecciona una carpeta con el botón *Examinar* o arrastrándola a la zona de drop.
2. Ajusta la tolerancia con el slider. Se recomienda un valor entre **80 y 90%**.
3. Pulsa **Ordenar Archivos**.
4. Revisa el panel de estado para ver qué archivos se movieron y cuáles no.
5. Opcionalmente, exporta el informe.

---

## 📁 Estructura del proyecto

> ⚠️ Actualmente todo el código reside en `Ordenar.py`. En un futuro próximo se separará la lógica en módulos independientes.

```
pinkcat-sort/
└── Ordenar.py
```

---

## ⚠️ Notas

- Solo se procesan los archivos en el **primer nivel** de la carpeta seleccionada, sin entrar en subcarpetas.
- Si un archivo no encuentra ninguna carpeta con suficiente similitud, aparecerá en la sección de archivos no movidos.
