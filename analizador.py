{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "140f053d-451f-47a3-8801-bb03cdbde8e9",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "from scipy.signal import butter, lfilter, cheby1, cheby2\n",
    "import tkinter as tk\n",
    "from tkinter import ttk\n",
    "from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg\n",
    "from matplotlib.figure import Figure\n",
    "from tkinter import filedialog\n",
    "import scipy.io.wavfile as wavfile\n",
    "\n",
    "# Parámetros iniciales\n",
    "N = 4096  # Número de muestras\n",
    "fs = 48000  # Frecuencia de muestreo por defecto\n",
    "\n",
    "# Variables para determinar si una señal es ideal o proviene de un archivo WAV\n",
    "es_ideal_onda1 = True\n",
    "es_ideal_onda2 = True\n",
    "\n",
    "# Variables globales para las señales\n",
    "onda1_original = None\n",
    "onda2_original = None\n",
    "fs1 = fs  # Frecuencia de muestreo de onda1\n",
    "fs2 = fs  # Frecuencia de muestreo de onda2\n",
    "\n",
    "# Función para crear las señales onda1 y onda2 con ganancia y polaridad\n",
    "def crear_ondas(N, ganancia_onda1_db, ganancia_onda2_db, polaridad_onda1, polaridad_onda2):\n",
    "    # Inicializar las señales\n",
    "    onda1 = np.zeros(N)  # Inicializar la señal Onda 1\n",
    "    onda2 = np.zeros(N)  # Inicializar la señal Onda 2\n",
    "\n",
    "    # Crear señales impulsionales con ganancia y polaridad aplicadas\n",
    "    onda1[0] = 10 ** (ganancia_onda1_db / 20) * np.cos(polaridad_onda1)\n",
    "    onda2[0] = 10 ** (ganancia_onda2_db / 20) * np.cos(polaridad_onda2)\n",
    "\n",
    "    return onda1, onda2\n",
    "\n",
    "# Función para cargar archivo WAV y sobrescribir la señal ideal\n",
    "def cargar_wav(canal):\n",
    "    global es_ideal_onda1, es_ideal_onda2, onda1_original, onda2_original\n",
    "    archivo_wav = filedialog.askopenfilename(filetypes=[(\"Archivos WAV\", \"*.wav\")])\n",
    "    \n",
    "    if archivo_wav:\n",
    "        try:\n",
    "            fs, data = wavfile.read(archivo_wav)\n",
    "\n",
    "            if len(data.shape) == 2:  # Señal estéreo\n",
    "                if canal == 1:\n",
    "                    data_canal = data[:, 0]\n",
    "                else:\n",
    "                    data_canal = data[:, 1]\n",
    "            else:  # Señal mono\n",
    "                data_canal = data\n",
    "            \n",
    "            if len(data_canal) > N:\n",
    "                data_canal = data_canal[:N]\n",
    "            elif len(data_canal) < N:\n",
    "                data_canal = np.pad(data_canal, (0, N - len(data_canal)), 'constant')\n",
    "\n",
    "            if canal == 1:\n",
    "                global onda1, fs1\n",
    "                fs1 = fs\n",
    "                onda1_original = data_canal  # Guardar la señal original para procesarla luego\n",
    "                onda1 = onda1_original.copy()  # Usar una copia de la señal original\n",
    "                es_ideal_onda1 = False  # Señal cargada desde WAV\n",
    "            else:\n",
    "                global onda2, fs2\n",
    "                fs2 = fs\n",
    "                onda2_original = data_canal  # Guardar la señal original para procesarla luego\n",
    "                onda2 = onda2_original.copy()  # Usar una copia de la señal original\n",
    "                es_ideal_onda2 = False  # Señal cargada desde WAV\n",
    "\n",
    "            actualizar_señales()\n",
    "        except Exception as e:\n",
    "            error_label.config(text=f\"Error al cargar el archivo WAV: {str(e)}\")\n",
    "\n",
    "def seleccionar_filtro(tipo_filtro, order, cutoff, fs, tipo, ripple=None, bandwidth=None):\n",
    "    if tipo_filtro == \"Butterworth\":\n",
    "        return butter(order, cutoff / (0.5 * fs), btype=tipo)\n",
    "    elif tipo_filtro == \"Chebyshev 1\":\n",
    "        if ripple is None:\n",
    "            ripple = 1  # Valor predeterminado de ripple si no se proporciona\n",
    "        return cheby1(order, ripple, cutoff / (0.5 * fs), btype=tipo)\n",
    "    elif tipo_filtro == \"Chebyshev 2\":\n",
    "        if ripple is None:\n",
    "            ripple = 40  # Valor predeterminado de ripple (atenuación) para Chebyshev 2\n",
    "        return cheby2(order, ripple, cutoff / (0.5 * fs), btype=tipo)\n",
    "    elif tipo_filtro == \"Linkwitz-Riley\":\n",
    "        return butter(order // 2, cutoff / (0.5 * fs), btype=tipo)\n",
    "    elif tipo_filtro == \"All Pass\":\n",
    "        if order == 1:\n",
    "            return all_pass_1st_order(cutoff, fs)\n",
    "        elif order == 2:\n",
    "            if bandwidth is None:\n",
    "                bandwidth = 0.707  # Usar bandwidth (Q) como factor de calidad para All Pass de segundo orden\n",
    "            return all_pass_2nd_order(cutoff, fs, bandwidth)\n",
    "        else:\n",
    "            raise ValueError(\"El filtro All Pass solo admite orden 1 o 2.\")\n",
    "    else:\n",
    "        raise ValueError(\"Tipo de filtro no válido\")\n",
    "\n",
    "def all_pass_1st_order(cutoff, fs):\n",
    "    omega = 2 * np.pi * cutoff / fs  # Frecuencia angular normalizada\n",
    "    alpha = (1 - np.sin(omega)) / np.cos(omega)\n",
    "    # Coeficientes del filtro All Pass de primer orden\n",
    "    b = [alpha, -1]\n",
    "    a = [1, -alpha]\n",
    "    return b, a\n",
    "\n",
    "def all_pass_2nd_order(cutoff, fs, Q=0.707):\n",
    "    omega = 2 * np.pi * cutoff / fs\n",
    "    alpha = np.sin(omega) / (2 * Q)\n",
    "\n",
    "    a0 = 1 + alpha\n",
    "    a1 = -2 * np.cos(omega)\n",
    "    a2 = 1 - alpha\n",
    "\n",
    "    b0 = a2\n",
    "    b1 = a1\n",
    "    b2 = a0\n",
    "\n",
    "    b = [b0 / a0, b1 / a0, b2 / a0]\n",
    "    a = [1, a1 / a0, a2 / a0]\n",
    "\n",
    "    return b, a\n",
    "    \n",
    "def obtener_ripple(entry):\n",
    "    try:\n",
    "        valor = float(entry.get())\n",
    "        if valor > 0:\n",
    "            return valor\n",
    "        else:\n",
    "            raise ValueError\n",
    "    except ValueError:\n",
    "        error_label.config(text=\"Valor de ripple no válido. Se usará el valor predeterminado de 1 dB.\")\n",
    "        return 1\n",
    "\n",
    "def obtener_bandwidth(entry):\n",
    "    try:\n",
    "        valor = float(entry.get())\n",
    "        if valor > 0:\n",
    "            return valor\n",
    "        else:\n",
    "            raise ValueError\n",
    "    except ValueError:\n",
    "        error_label.config(text=\"Valor de ancho de banda no válido. Se usará el valor predeterminado de 0.707.\")\n",
    "        return 0.707\n",
    "\n",
    "def obtener_orden_filtro(entry):\n",
    "    try:\n",
    "        valor = int(entry.get())\n",
    "        if valor >= 1:  # Solo aceptamos valores enteros positivos\n",
    "            return valor\n",
    "        else:\n",
    "            raise ValueError\n",
    "    except ValueError:\n",
    "        error_label.config(text=\"Orden no válido. Se usará el valor predeterminado de 1.\")\n",
    "        return 1  # Valor predeterminado si no es válido\n",
    "\n",
    "def aplicar_delay(signal, fs, delay_ms):\n",
    "    delay_samples = int(delay_ms * fs / 1000)\n",
    "    if delay_samples == 0:\n",
    "        return signal\n",
    "    delayed_signal = np.zeros_like(signal)\n",
    "    if delay_samples < len(signal):\n",
    "        delayed_signal[delay_samples:] = signal[:-delay_samples]\n",
    "    return delayed_signal\n",
    "\n",
    "def obtener_delay_desde_texto(texto):\n",
    "    try:\n",
    "        valor = float(texto.get())\n",
    "        return valor if valor >= 0 else 0\n",
    "    except ValueError:\n",
    "        return 0.0\n",
    "\n",
    "def obtener_frecuencia_corte(entry):\n",
    "    try:\n",
    "        valor = float(entry.get())\n",
    "        if 20 <= valor <= 20000:\n",
    "            return valor\n",
    "        else:\n",
    "            raise ValueError\n",
    "    except ValueError:\n",
    "        if entry.get().strip() == \"\":  # Si el campo está vacío\n",
    "            return 20  # Valor predeterminado\n",
    "        error_label.config(text=\"Frecuencia no válida. Se usará el valor predeterminado de 20 Hz.\")\n",
    "        return 20\n",
    "\n",
    "# Función para actualizar las señales y aplicar transformaciones\n",
    "def actualizar_señales(*args):\n",
    "    global onda1, onda2, es_ideal_onda1, es_ideal_onda2\n",
    "\n",
    "    error_label.config(text=\"\")  # Limpiar mensaje de error\n",
    "\n",
    "    # Usar las frecuencias de muestreo correspondientes (si se ha cargado WAV o usar por defecto)\n",
    "    fs_onda1 = fs1 if not es_ideal_onda1 else fs\n",
    "    fs_onda2 = fs2 if not es_ideal_onda2 else fs\n",
    "\n",
    "    # Obtener valores de la interfaz\n",
    "    ganancia_onda1_db = ganancia1_scale.get()\n",
    "    ganancia_onda2_db = ganancia2_scale.get()\n",
    "    polaridad_onda1 = 0 if polaridad1_var.get() == \"0\" else np.pi\n",
    "    polaridad_onda2 = 0 if polaridad2_var.get() == \"0\" else np.pi\n",
    "\n",
    "    filtro1_tipo = filtro1_var.get()\n",
    "    filtro2_tipo = filtro2_var.get()\n",
    "    tipo1_filtro = tipo1_var.get()\n",
    "    tipo2_filtro = tipo2_var.get()\n",
    "\n",
    "    orden1 = obtener_orden_filtro(orden1_entry)\n",
    "    orden2 = obtener_orden_filtro(orden2_entry)\n",
    "\n",
    "    cutoff1 = obtener_frecuencia_corte(cutoff1_entry)\n",
    "    cutoff2 = obtener_frecuencia_corte(cutoff2_entry)\n",
    "\n",
    "    delay1_ms = obtener_delay_desde_texto(delay1_text)\n",
    "    delay2_ms = obtener_delay_desde_texto(delay2_text)\n",
    "\n",
    "    ripple1 = obtener_ripple(riple_entry) if \"Chebyshev\" in filtro1_tipo else None\n",
    "    ripple2 = obtener_ripple(riple_entry) if \"Chebyshev\" in filtro2_tipo else None\n",
    "\n",
    "    bandwidth1 = obtener_bandwidth(bandwidth_entry) if filtro1_var.get() == \"All Pass\" else None\n",
    "    bandwidth2 = obtener_bandwidth(bandwidth_entry) if filtro2_var.get() == \"All Pass\" else None\n",
    "\n",
    "    # Restaurar la señal original antes de aplicar el filtro\n",
    "    if es_ideal_onda1:\n",
    "        onda1, _ = crear_ondas(N, ganancia_onda1_db, 0, polaridad_onda1, 0)\n",
    "    else:\n",
    "        onda1 = onda1_original.copy()  # Restaurar la señal original cargada desde el archivo\n",
    "\n",
    "    if es_ideal_onda2:\n",
    "        _, onda2 = crear_ondas(N, 0, ganancia_onda2_db, 0, polaridad_onda2)\n",
    "    else:\n",
    "        onda2 = onda2_original.copy()  # Restaurar la señal original cargada desde el archivo\n",
    "\n",
    "    # Aplicar ganancia y polaridad\n",
    "    # Crear señales impulsionales con ganancia y polaridad aplicadas\n",
    "    onda1 = np.zeros(N)\n",
    "    onda2 = np.zeros(N)\n",
    "    onda1[0] = 10 ** (ganancia_onda1_db / 20) * np.cos(polaridad_onda1)\n",
    "    onda2[0] = 10 ** (ganancia_onda2_db / 20) * np.cos(polaridad_onda2)\n",
    "\n",
    "    # Aplicar filtro a Onda 1\n",
    "    if filtro1_tipo != \"none\":\n",
    "        b, a = seleccionar_filtro(filtro1_tipo, orden1, cutoff1, fs_onda1, tipo1_filtro, ripple=ripple1, bandwidth=bandwidth1)\n",
    "        onda1 = lfilter(b, a, onda1)\n",
    "\n",
    "    # Aplicar filtro a Onda 2\n",
    "    if filtro2_tipo != \"none\":\n",
    "        b, a = seleccionar_filtro(filtro2_tipo, orden2, cutoff2, fs_onda2, tipo2_filtro, ripple=ripple2, bandwidth=bandwidth2)\n",
    "        onda2 = lfilter(b, a, onda2)\n",
    "\n",
    "    # Aplicar el delay a ambas señales\n",
    "    onda1 = aplicar_delay(onda1, fs_onda1, delay1_ms)\n",
    "    onda2 = aplicar_delay(onda2, fs_onda2, delay2_ms)\n",
    "\n",
    "    # FFT de las ondas para obtener magnitud y fase\n",
    "    fft_onda1 = np.fft.fft(onda1)\n",
    "    fft_onda2 = np.fft.fft(onda2)\n",
    "\n",
    "    # Calcular la suma y el promedio de las señales\n",
    "    suma_ondas = onda1 + onda2\n",
    "    promedio_ondas = (onda1 + onda2) / 2\n",
    "\n",
    "    # FFT de la sumatoria y promedio\n",
    "    fft_suma = np.fft.fft(suma_ondas)\n",
    "    fft_promedio = np.fft.fft(promedio_ondas)\n",
    "\n",
    "    # Magnitud y fase\n",
    "    magnitud_onda1 = np.abs(fft_onda1)\n",
    "    magnitud_onda2 = np.abs(fft_onda2)\n",
    "    magnitud_suma = np.abs(fft_suma)\n",
    "    magnitud_promedio = np.abs(fft_promedio)\n",
    "\n",
    "    fase_onda1 = np.angle(fft_onda1) * 180 / np.pi\n",
    "    fase_onda2 = np.angle(fft_onda2) * 180 / np.pi\n",
    "    fase_suma = np.angle(fft_suma) * 180 / np.pi\n",
    "    fase_promedio = np.angle(fft_promedio) * 180 / np.pi\n",
    "\n",
    "    frequencies = np.fft.fftfreq(N, 1/fs_onda1)\n",
    "\n",
    "    # Filtrar las frecuencias para mostrar solo de 20 Hz a 20 kHz\n",
    "    min_freq = 20\n",
    "    max_freq = 20000\n",
    "    idx = np.where((frequencies >= min_freq) & (frequencies <= max_freq))\n",
    "\n",
    "    # Limpiar los ejes antes de volver a dibujar\n",
    "    ax1.clear()\n",
    "    ax2.clear()\n",
    "\n",
    "    epsilon = 1e-10\n",
    "\n",
    "    # Gráfica combinada de Magnitud en escala logarítmica\n",
    "    ax1.semilogx(frequencies[idx], 20 * np.log10(magnitud_onda1[idx] + epsilon), label='Onda 1')\n",
    "    ax1.semilogx(frequencies[idx], 20 * np.log10(magnitud_onda2[idx] + epsilon), label='Onda 2')\n",
    "    ax1.semilogx(frequencies[idx], 20 * np.log10(magnitud_suma[idx] + epsilon), label='Suma')\n",
    "    ax1.semilogx(frequencies[idx], 20 * np.log10(magnitud_promedio[idx] + epsilon), label='Promedio')\n",
    "    ax1.axhline(-3, color='black', linestyle='--', linewidth=0.7)  # Línea de -3 dB\n",
    "    ax1.set_xlabel('Frecuencia (Hz)')\n",
    "    ax1.set_xlim([20, 20000])\n",
    "    ax1.set_ylabel('Magnitud (dB)')\n",
    "    ax1.set_title(\"Magnitud de las Ondas [dB]\")\n",
    "    ax1.legend()\n",
    "    ax1.grid(True)\n",
    "\n",
    "    xtick_labels = [31.5, 63, 125, 250, 500, 1000, 4000, 8000, 16000]\n",
    "    xtick_labels_str = ['31.5', '63', '125', '250', '500', '1k', '4k', '8k', '16k']\n",
    "\n",
    "    ax1.set_xticks(xtick_labels)\n",
    "    ax1.set_xticklabels(xtick_labels_str)\n",
    "\n",
    "    # Gráfica combinada de Fase\n",
    "    ax2.semilogx(frequencies[idx], fase_onda1[idx], label='Onda 1')\n",
    "    ax2.semilogx(frequencies[idx], fase_onda2[idx], label='Onda 2')\n",
    "    ax2.semilogx(frequencies[idx], fase_suma[idx], label='Suma')\n",
    "    ax2.semilogx(frequencies[idx], fase_promedio[idx], label='Promedio')\n",
    "    ax2.set_xlabel('Frecuencia (Hz)')\n",
    "    ax2.set_yticks([-180, -135, -90, -45, 0, 45, 90, 135, 180])\n",
    "    ax2.set_xlim([20, 20000])\n",
    "    ax2.set_ylim([-185, 185])\n",
    "    ax2.set_ylabel('Fase (°)')\n",
    "    ax2.set_title(\"Fase de las Ondas (Grados)\")\n",
    "    ax2.legend()\n",
    "    ax2.grid(True)\n",
    "    ax2.set_xticks(xtick_labels)\n",
    "    ax2.set_xticklabels(xtick_labels_str)\n",
    "\n",
    "    # Ajustar el layout para evitar la sobreposición\n",
    "    fig.tight_layout()\n",
    "\n",
    "    # Redibujar los gráficos\n",
    "    canvas.draw()\n",
    "\n",
    "\n",
    "# Configuración de la interfaz gráfica con Tkinter\n",
    "root = tk.Tk()\n",
    "root.title(\"Control de Señales\")\n",
    "\n",
    "# Establecer el color del texto de los Combobox a negro\n",
    "style = ttk.Style()\n",
    "style.configure(\"TCombobox\", foreground=\"black\")\n",
    "\n",
    "root.geometry(\"1440x900\")\n",
    "\n",
    "# Crear figura y ejes para la gráfica\n",
    "fig = Figure(figsize=(9, 7))\n",
    "ax1 = fig.add_subplot(2, 1, 1)\n",
    "ax2 = fig.add_subplot(2, 1, 2)\n",
    "\n",
    "ax1.set_xlabel('Frecuencia (Hz)')\n",
    "ax1.set_ylabel('Magnitud (dB)')\n",
    "ax1.grid(True)\n",
    "\n",
    "ax2.set_xlabel('Frecuencia (Hz)')\n",
    "ax2.set_ylabel('Fase (°)')\n",
    "ax2.grid(True)\n",
    "\n",
    "fig.tight_layout()\n",
    "\n",
    "canvas = FigureCanvasTkAgg(fig, master=root)\n",
    "canvas.draw()\n",
    "canvas.get_tk_widget().grid(row=0, column=2, rowspan=14, padx=10, pady=10, sticky=\"nsew\")\n",
    "\n",
    "tk.Label(root, text=\"Ganancia Onda 1 (dB)\").grid(row=0, column=0, sticky=\"w\", padx=10)\n",
    "ganancia1_scale = tk.Scale(root, from_=-30, to=30, resolution=1, orient=\"horizontal\")\n",
    "ganancia1_scale.set(0)\n",
    "ganancia1_scale.grid(row=0, column=1, padx=10, pady=5)\n",
    "ganancia1_scale.bind(\"<ButtonRelease-1>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Ganancia Onda 2 (dB)\").grid(row=1, column=0, sticky=\"w\", padx=10)\n",
    "ganancia2_scale = tk.Scale(root, from_=-30, to=30, resolution=1, orient=\"horizontal\")\n",
    "ganancia2_scale.set(0)\n",
    "ganancia2_scale.grid(row=1, column=1, padx=10, pady=5)\n",
    "ganancia2_scale.bind(\"<ButtonRelease-1>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Polaridad Onda 1\").grid(row=2, column=0, sticky=\"w\", padx=10)\n",
    "polaridad1_var = tk.StringVar(value=\"0\")\n",
    "ttk.Combobox(root, textvariable=polaridad1_var, values=[\"0\", \"180º\"]).grid(row=2, column=1, padx=10)\n",
    "polaridad1_var.trace(\"w\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Polaridad Onda 2\").grid(row=3, column=0, sticky=\"w\", padx=10)\n",
    "polaridad2_var = tk.StringVar(value=\"0\")\n",
    "ttk.Combobox(root, textvariable=polaridad2_var, values=[\"0\", \"180º\"]).grid(row=3, column=1, padx=10)\n",
    "polaridad2_var.trace(\"w\", actualizar_señales)\n",
    "\n",
    "# Filtro y orden para Onda 1\n",
    "tk.Label(root, text=\"Filtro Onda 1\").grid(row=4, column=0, sticky=\"w\", padx=10)\n",
    "filtro1_var = tk.StringVar(value=\"none\")\n",
    "ttk.Combobox(root, textvariable=filtro1_var, values=[\"none\", \"Butterworth\", \"Chebyshev 1\", \"Chebyshev 2\", \"Linkwitz-Riley\", \"All Pass\"], style=\"TCombobox\").grid(row=4, column=1, padx=10)\n",
    "filtro1_var.trace(\"w\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Orden Filtro Onda 1\").grid(row=5, column=0, sticky=\"w\", padx=10)\n",
    "orden1_entry = tk.Entry(root)\n",
    "orden1_entry.grid(row=5, column=1, padx=10)\n",
    "orden1_entry.insert(0, \"1\")\n",
    "orden1_entry.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Frecuencia de Corte Onda 1 (Hz)\").grid(row=6, column=0, sticky=\"w\", padx=10)\n",
    "cutoff1_entry = tk.Entry(root)\n",
    "cutoff1_entry.grid(row=6, column=1, padx=10)\n",
    "cutoff1_entry.insert(0, \"1000\")\n",
    "cutoff1_entry.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Tipo de Paso Onda 1\").grid(row=7, column=0, sticky=\"w\", padx=10)\n",
    "tipo1_var = tk.StringVar(value=\"none\")\n",
    "ttk.Combobox(root, textvariable=tipo1_var, values=[\"none\", \"lowpass\", \"highpass\"], style=\"TCombobox\").grid(row=7, column=1, padx=10)\n",
    "tipo1_var.trace(\"w\", actualizar_señales)\n",
    "\n",
    "# Filtro y orden para Onda 2\n",
    "tk.Label(root, text=\"Filtro Onda 2\").grid(row=8, column=0, sticky=\"w\", padx=10)\n",
    "filtro2_var = tk.StringVar(value=\"none\")\n",
    "ttk.Combobox(root, textvariable=filtro2_var, values=[\"none\", \"Butterworth\", \"Chebyshev 1\", \"Chebyshev 2\", \"Linkwitz-Riley\", \"All Pass\"], style=\"TCombobox\").grid(row=8, column=1, padx=10)\n",
    "filtro2_var.trace(\"w\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Orden Filtro Onda 2\").grid(row=9, column=0, sticky=\"w\", padx=10)\n",
    "orden2_entry = tk.Entry(root)\n",
    "orden2_entry.grid(row=9, column=1, padx=10)\n",
    "orden2_entry.insert(0, \"1\")\n",
    "orden2_entry.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Frecuencia de Corte Onda 2 (Hz)\").grid(row=10, column=0, sticky=\"w\", padx=10)\n",
    "cutoff2_entry = tk.Entry(root)\n",
    "cutoff2_entry.grid(row=10, column=1, padx=10)\n",
    "cutoff2_entry.insert(0, \"1000\")\n",
    "cutoff2_entry.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Tipo de Paso Onda 2\").grid(row=11, column=0, sticky=\"w\", padx=10)\n",
    "tipo2_var = tk.StringVar(value=\"none\")\n",
    "ttk.Combobox(root, textvariable=tipo2_var, values=[\"none\", \"lowpass\", \"highpass\"], style=\"TCombobox\").grid(row=11, column=1, padx=10)\n",
    "tipo2_var.trace(\"w\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Delay Onda 1 (ms)\").grid(row=12, column=0, sticky=\"w\", padx=10)\n",
    "delay1_text = tk.Entry(root)\n",
    "delay1_text.grid(row=12, column=1, padx=10)\n",
    "delay1_text.insert(0, \"0\")\n",
    "delay1_text.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Delay Onda 2 (ms)\").grid(row=13, column=0, sticky=\"w\", padx=10)\n",
    "delay2_text = tk.Entry(root)\n",
    "delay2_text.grid(row=13, column=1, padx=10)\n",
    "delay2_text.insert(0, \"0\")\n",
    "delay2_text.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Ancho de Banda\").grid(row=14, column=0, sticky=\"w\", padx=10)\n",
    "bandwidth_entry = tk.Entry(root)\n",
    "bandwidth_entry.grid(row=14, column=1, padx=10)\n",
    "bandwidth_entry.insert(0, \"1\")\n",
    "bandwidth_entry.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Ripple\").grid(row=15, column=0, sticky=\"w\", padx=10)\n",
    "riple_entry = tk.Entry(root)\n",
    "riple_entry.grid(row=15, column=1, padx=10)\n",
    "riple_entry.insert(0, \"1\")\n",
    "riple_entry.bind(\"<KeyRelease>\", actualizar_señales)\n",
    "\n",
    "tk.Label(root, text=\"Cargar WAV Onda 1\").grid(row=16, column=0, sticky=\"w\", padx=10)\n",
    "boton_wav_onda1 = tk.Button(root, text=\"Cargar WAV\", command=lambda: cargar_wav(1))\n",
    "boton_wav_onda1.grid(row=16, column=1, padx=10, pady=5)\n",
    "\n",
    "tk.Label(root, text=\"Cargar WAV Onda 2\").grid(row=17, column=0, sticky=\"w\", padx=10)\n",
    "boton_wav_onda2 = tk.Button(root, text=\"Cargar WAV\", command=lambda: cargar_wav(2))\n",
    "boton_wav_onda2.grid(row=17, column=1, padx=10, pady=5)\n",
    "\n",
    "error_label = tk.Label(root, text=\"\", fg=\"red\")\n",
    "error_label.grid(row=17, column=1)\n",
    "\n",
    "actualizar_señales()\n",
    "\n",
    "root.mainloop()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "09e8df72-fd86-4277-b487-824c32dc4550",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "464942a6-df6c-48ea-a5a7-6db6dc28d17e",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
