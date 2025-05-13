# Introducción a la Ciencia de Datos 2025 - Tarea 1

Integrantes: 
- Diego Del Po
- Julian O'Flaherty

# Descripción

Este repositorio contiene el informe, así como los scripts de python usados para la realización de la tarea 1.

El informe se encuentra en el archivo `informe.pdf`.

# Cómo ejecutar los scripts

Para ejecutar los scripts, primero es necesario instalar las dependencias.
Sugerimos crear un ambiente virtual.
```bash
python -m venv .venv
source .venv/bin/activate
```

Luego, es necesario instalar las dependencias.
```bash
pip install -r requirements.txt
```

Para generar todas las imágenes, es necesario ejecutar el siguiente comando. Las imágenes quedarán guardadas en la carpeta `img` del proyecto.
```bash
python utils/tarea_1.py
```

Este script es el que orquesta toda la tarea en general. El script `clean_data.py` contiene funciones para limpiar texto. El script `plots.py` contiene los gráficos. Y el script `location_analysis.py` tiene un análisis de la columna `location` del set de datos.