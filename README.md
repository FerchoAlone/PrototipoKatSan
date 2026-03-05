# AppReportes - Reconocimiento de Emociones en Tiempo Real

Aplicacion en Python para detectar emociones faciales en tiempo real desde webcam, grabar sesiones de video y generar reportes en Excel (tecnico y no tecnico) con trazabilidad temporal de las clasificaciones.

## Tabla de contenido

- [AppReportes - Reconocimiento de Emociones en Tiempo Real](#appreportes---reconocimiento-de-emociones-en-tiempo-real)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Descripcion general](#descripcion-general)
  - [Arquitectura del proyecto](#arquitectura-del-proyecto)
  - [Estructura de carpetas](#estructura-de-carpetas)
  - [Requisitos](#requisitos)
  - [Configuracion local](#configuracion-local)
    - [1) Clonar repositorio](#1-clonar-repositorio)
    - [2) Crear entorno virtual](#2-crear-entorno-virtual)
    - [3) Instalar dependencias](#3-instalar-dependencias)
    - [4) Verificar archivos de modelo](#4-verificar-archivos-de-modelo)
  - [Ejecucion](#ejecucion)
  - [Uso durante la sesion](#uso-durante-la-sesion)
  - [Salida generada](#salida-generada)
    - [Reporte tecnico](#reporte-tecnico)
    - [Reporte no tecnico](#reporte-no-tecnico)
  - [Personalizacion](#personalizacion)
  - [Problemas comunes](#problemas-comunes)

## Descripcion general

El proyecto integra:

- Deteccion de rostro con MediaPipe (`detector.tflite`).
- Clasificacion de emociones mediante un ensamble:
- `MobileNetV2LSTM.keras`
- `MobileNetV3LargeLSTM.keras`
- Meta-modelo `XGBoost` (`meta_model_xgboost.pkl`)
- Visualizacion en tiempo real de Top-1 y Top-2 emociones.
- Grabacion de video de sesion.
- Generacion automatica de reportes Excel con resumen, distribucion y linea de tiempo emocional.

## Arquitectura del proyecto

Flujo principal:

1. `app.py` inicia el sistema.
2. `ensemble_pipeline.py` carga y prepara el modelo de ensamble.
3. `core/runtime.py` toma frames de camara, detecta rostro y ejecuta inferencia por ventana temporal.
4. `core/recording.py` administra inicio/fin de grabacion y eventos de clasificacion.
5. `core/reporting.py` crea reportes Excel tecnicos y no tecnicos.

## Estructura de carpetas

```text
AppReportes/
|-- app.py
|-- ensemble_pipeline.py
|-- emotion_map.py
|-- requirements.txt
|-- core/
|   |-- config.py          # Parametros globales
|   |-- face_detection.py  # Deteccion y recorte de rostro
|   |-- runtime.py         # Loop principal de procesamiento
|   |-- recording.py       # Grabacion y registro de eventos
|   |-- reporting.py       # Exportacion de reportes Excel
|   `-- ui.py              # Overlay visual en pantalla
|-- model/
|   |-- detector.tflite
|   |-- MobileNetV2LSTM.keras
|   |-- MobileNetV3LargeLSTM.keras
|   `-- meta_model_xgboost.pkl
`-- recordings/
    `-- YYYYMMDD_HHMMSS/
        |-- grabacion.mp4
        |-- informe_emociones_tecnico.xlsx
        `-- informe_emociones_no_tecnico.xlsx
```

## Requisitos

- Python 3.10 recomendado.
- Webcam funcional.
- SO compatible: Windows, Linux o macOS.

Dependencias principales (ver `requirements.txt`):

- `tensorflow`
- `keras`
- `mediapipe`
- `opencv-python`
- `xgboost`
- `openpyxl`
- `numpy`
- `joblib`

## Configuracion local

### 1) Clonar repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd AppReportes
```

### 2) Crear entorno virtual

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Verificar archivos de modelo

Asegurese de tener estos archivos dentro de `model/`:

- `detector.tflite`
- `MobileNetV2LSTM.keras`
- `MobileNetV3LargeLSTM.keras`
- `meta_model_xgboost.pkl`

Sin estos archivos, la aplicacion no podra iniciar inferencia.

## Ejecucion

Desde la raiz del proyecto:

```bash
python app.py
```

Si todo esta correcto, se abrira una ventana con la camara y overlay de emociones.

## Uso durante la sesion

Controles de teclado:

- `S`: iniciar/detener grabacion.
- `Q`: salir de la aplicacion.

Comportamiento:

- Al iniciar grabacion, se crea una carpeta timestamp en `recordings/`.
- Durante la grabacion se registra video y eventos de prediccion (Top-1/Top-2 + confianza + tiempo).
- Al detener, se generan automaticamente los reportes Excel.

## Salida generada

Por cada sesion grabada (`recordings/YYYYMMDD_HHMMSS/`):

- `grabacion.mp4`
- `informe_emociones_tecnico.xlsx`
- `informe_emociones_no_tecnico.xlsx`

### Reporte tecnico

Incluye:

- Resumen cuantitativo de la sesion.
- Clasificaciones por evento (tiempo, emociones, confianza).
- Distribucion de emociones principales y secundarias.
- Linea de tiempo emocional con grafico.
- Notas de interpretacion.

### Reporte no tecnico

Incluye:

- Resumen simplificado.
- Nivel de presencia emocional (alta/media/baja).
- Mensaje interpretativo general.
- Linea de tiempo emocional simplificada.

## Personalizacion

Los parametros se ajustan en `core/config.py`:

- `camera_index`: camara a usar.
- `face_scale`: escala del bounding box facial.
- `face_size`: resolucion de recorte para inferencia.
- `default_camera_fps`: FPS por defecto para grabacion.
- nombres de archivos de salida y carpeta raiz de grabaciones.

Tambien puede ajustar frecuencia de inferencia en `core/runtime.py`:

- `seq_len` (longitud de secuencia temporal).
- `predict_every` (cada cuantos frames predecir).

## Problemas comunes

- Error al abrir camara:
  - valide que no este ocupada por otra aplicacion.
  - pruebe otro indice (`camera_index`) en `core/config.py`.

- Error por modelos faltantes:
  - verifique la carpeta `model/` y nombres exactos de archivos.

- Error por dependencia faltante (`openpyxl`, `mediapipe`, etc.):
  - ejecute nuevamente `pip install -r requirements.txt`.

- Rendimiento bajo:
  - reduzca resolucion de camara o cierre aplicaciones en paralelo.
  - aumente `predict_every` para inferir con menos frecuencia.