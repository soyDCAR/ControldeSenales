# 🎚️ Analizador de Señales de Audio con Filtros Digitales

Esta es una aplicación interactiva escrita en Python que permite visualizar y analizar señales de audio (impulsos o archivos WAV) mediante transformaciones como ganancia, polaridad, filtros digitales y delay. Se muestran en tiempo real las respuestas en frecuencia (magnitud y fase) de las señales individuales y su combinación.

## 🖼️ Captura de Pantalla

> *(Agrega aquí una imagen de la interfaz si lo deseas)*

---

## 🚀 Características

- ✅ Generación de señales impulsionales ideales.
- ✅ Carga de archivos `.wav` mono o estéreo.
- ✅ Control de **ganancia** (±30 dB).
- ✅ Control de **polaridad** (0° o 180°).
- ✅ Aplicación de **filtros digitales**:
  - Butterworth
  - Chebyshev Tipo I
  - Chebyshev Tipo II
  - Linkwitz-Riley
  - All Pass (orden 1 y 2)
- ✅ Simulación de **retardo (delay)** en milisegundos.
- ✅ Visualización de:
  - Magnitud en dB (escala logarítmica)
  - Fase en grados
  - Señales individuales, suma y promedio
- ✅ Interfaz gráfica amigable con **Tkinter** y gráficos con **Matplotlib**.

---

## 📦 Requisitos

Instala las siguientes bibliotecas de Python si no las tienes:

```bash
pip install numpy scipy matplotlib
````

---

## ▶️ Cómo Ejecutar

1. Guarda el archivo.
2. Ejecuta con Python 3:

```bash
python analizador.py
```

---

## 📁 Estructura del Proyecto

```
analizador.py         # Archivo principal de la aplicación
README.md             # Este archivo
```

---

## 🛠️ Uso

* Ajusta los controles desde la interfaz gráfica.
* Puedes cargar tus propios archivos `.wav`.
* Observa cómo cambian la magnitud y fase de las señales aplicando diferentes filtros o retardo.
* Ideal para estudiantes, ingenieros de audio y pruebas de cancelación de fase o diseño de filtros.

---

## 📚 Créditos

Desarrollado usando:

* [Tkinter](https://docs.python.org/3/library/tkinter.html)
* [NumPy](https://numpy.org/)
* [SciPy](https://scipy.org/)
* [Matplotlib](https://matplotlib.org/)

---


