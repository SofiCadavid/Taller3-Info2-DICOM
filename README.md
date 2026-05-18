# Taller 3 — Informática II

**Introducción a la informática médica — Procesamiento de archivos DICOM**

Universidad de Antioquia · Facultad de Ingeniería · Bioingeniería  
Monitor: Juan Esteban Pineda Lopera

---

## 1. Integrantes

- Sofia Cadavid Castro
- Gabriela Sanin Vera

---

## 2. Descripción del proyecto

Este proyecto ayuda a automatizar la lectura, extracción de datos y procesamiento básico de imágenes médicas en formato **DICOM**.

### Dataset utilizado

Para este taller utilizamos el dataset **MRI_Dicom_Scans** disponible extraído de la plataforma "Kaggle", que contiene resonancias magnéticas cerebrales en formato DICOM, divididas en `train`, `test` y `validation`. La carpeta también incluye archivos `.jpg` y `.png` que fueron descartados automáticamente por la aplicación.

Al ejecutar la aplicación sobre la carpeta `data/` completa se obtuvieron:

| Indicador            | Valor |
| -------------------- | ----- |
| Archivos revisados   | 1188  |
| DICOM válidos        | 886   |
| Archivos descartados | 302   |
| Imágenes procesadas  | 886   |
| Imágenes omitidas    | 0     |

Todos los DICOM válidos del dataset son de modalidad **MR** (resonancia magnética) con resolución típica de 256 × 256.

---

## 3. Cómo ejecutar el proyecto

### 3.1 Requisitos

- Python 3.10 o superior.
- Pip actualizado.
- Sistema operativo: Windows, Linux o macOS.

### 3.2 Pasos para ejecutar el proyecto

**1) Clonar el repositorio**

```bash
git clone https://github.com/SofiCadavid/Taller3-Info2-DICOM
cd Taller_3__Informática_2
```

**2) Crear y activar el entorno virtual**

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

En Linux o macOS:

```bash
python -m venv venv
source venv/bin/activate
```

**3) Instalar las librerías requeridas**

```bash
pip install pydicom
pip install numpy
pip install pandas
pip install opencv-python
pip install matplotlib
```

**4) Colocar los archivos DICOM**

Ubica los archivos DICOM dentro de la carpeta `data/`.

**5) Ejecutar el programa**

```bash
python main.py
```

Al terminar, los resultados quedarán dentro de la carpeta `results/`.

---

## 4. Informe y discusión

### 4.1 ¿Por qué DICOM y HL7 son cruciales para la interoperabilidad en salud y en qué se diferencian conceptualmente?

**DICOM** (_Digital Imaging and Communications in Medicine_) y **HL7** (_Health Level Seven_) son los dos estándares fundamentales que permiten que los sistemas hospitalarios "hablen el mismo idioma".

**¿Por qué son cruciales?**

- Un hospital moderno trabaja con decenas de fabricantes distintos ya sean resonadores Siemens, ecógrafos GE, software de historia clínica de un proveedor cualquiera, sistema de facturación de un proveedor o etc. Sin estándares, cada integración punto a punto sería muy costosa, frágil y propensa a errores que terminarían afectando la atención de cada paciente.
- Permiten que un estudio realizado en un equipo se visualice en cualquier estación de trabajo y se archive en cualquier PACS, sin importar el fabricante.
- Garantizan que la información clínica (alergias, medicación, resultados de laboratorio) viaje íntegra entre el sistema de admisiones, el de farmacia, el de imágenes y la historia clínica electrónica.
- Mejoran la seguridad del paciente al reducir errores manuales de transcripción y unificar identificadores.

**¿En qué se diferencian conceptualmente?**

Para responder a esta pregunta, nos ayudamos ilustrando la siguiente tabla:

| Aspecto                | DICOM                                                                              | HL7                                                                                          |
| ---------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Dominio principal      | Imagen médica (radiología, cardiología, oncología, etc.)                           | Datos clínicos y administrativos (admisiones, órdenes, resultados, dispensación)             |
| Contenido del mensaje  | Píxeles + datos del estudio en una sola "cápsula" (`.dcm`)                     | Texto estructurado: mensajes (v2.x con _pipes_) o recursos JSON/XML (FHIR)                   |
| Tipos de datos típicos | Imágenes 2D/3D/4D, formas de onda, informes estructurados                          | Demografía del paciente, alergias, medicamentos, resultados de laboratorio, órdenes médicas  |
| Protocolo de red       | DICOM over TCP (puertos DIMSE: C-STORE, C-FIND, C-MOVE) o DICOMweb (REST sobre HTTP) | MLLP (v2), HTTP/REST (FHIR)                                                                  |

**En resumen:** DICOM transporta la imagen y todo lo necesario para entenderla, mientras que HL7 transporta el resto del contexto clínico del paciente. Normalmente suelen existir al mismo tiempo, el RIS envía la orden por HL7, la modalidad adquiere la imagen y la archiva por DICOM, el PACS notifica vía HL7 que el estudio está disponible, y el informe radiológico vuelve al EMR otra vez por HL7.

### 6.2 Ventajas y limitaciones de la ecualización de histograma y la detección de bordes con Canny en imágenes médicas

**Ecualización del histograma**

_Ventajas de ecualizar el histograma:_

- Ayuda a mejorar el contraste global redistribuyendo las intensidades en todo el rango, lo cual ayuda a que sean visibles estructuras que en la imagen original aparecían en una franja estrecha de grises.
- Es una operación rápida y determinística, fácil de incorporar como paso de preprocesamiento.
- Útil cuando la imagen está subexpuesta o el detector tiene una respuesta logarítmica.

_Limitaciones de ecualizar el histograma:_

- Es una transformación **global**: aplica la misma curva a toda la imagen, por lo que puede saturar regiones brillantes, tales como: huesos en TAC, calcificaciones, y oscurecer detalles que ya tenían buen contraste desde un principio.
- **Amplifica el ruido** en zonas homogéneas, lo que es problemático en imágenes con bajo SNR (resonancia, ultrasonido).
- Puede **distorsionar la información cuantitativa**: los valores de píxel ecualizados ya no representan unidades físicas por lo que **no debe usarse para diagnóstico cuantitativo** sino solo para visualización o preprocesamiento previo a otros algoritmos.
- Genera resultados poco predecibles cuando la imagen tiene un histograma bimodal claro, por ejemplo, fondo negro con tejido, pudiendo "estirar" el fondo a costa del tejido.

> **Una alternativa común en imágenes médicas podría ser:** _CLAHE_ (Contrast Limited Adaptive Histogram Equalization), que opera por bloques y limita la amplificación del ruido.

**Detección de bordes con Canny**

_Ventajas:_

- Bordes finos (de 1 píxel de ancho), gracias a la supresión no máxima.
- Robustez al ruido por su suavizado gaussiano previo.
- La doble umbralización con histéresis permite distinguir bordes "fuertes" de bordes "débiles" conectados a fuertes, lo que reduce falsos positivos.
- Útil para resaltar contornos anatómicos (cráneo, ventrículos, lesiones con bordes definidos) como paso previo a segmentación o registro.

_Limitaciones:_

- **Muy sensible a los umbrales y a la varianza del filtro gaussiano**: parámetros que funcionan bien en una secuencia (por ejemplo T1) pueden fallar en otra (T2, FLAIR) o en otra modalidad.
- En tejidos con bordes difusos (transición sustancia gris/blanca, tumores infiltrativos) Canny produce bordes fragmentados o falsos.
- Detecta bordes como entidades binarias (hay/no hay), perdiendo información de magnitud o dirección que sí preservan algoritmos como Sobel, Scharr o Laplacian-of-Gaussian.
- No discrimina entre bordes clínicamente relevantes y artefactos (movimiento, suciedad del detector, ruido de adquisición).

**¿En qué escenarios clínicos puede ser útil o perjudicial?**

Nuevamnete, se presentan los escenarios en la siguiente tabla

| Escenario                                                                                                          | Útil / Perjudicial |
| ------------------------------------------------------------------------------------------------------------------ | ------------------ |
| Visualización previa al diagnóstico para resaltar el contraste de partes blandas en una radiografía digital        | ÚTIL               |
| Preprocesamiento para algoritmos clásicos de segmentación (umbralización, contornos activos)                       | ÚTIL               |
| Preparación de datasets para entrenar modelos de _deep learning_ que requieren consistencia visual                  | ÚTIL |
| Diagnóstico cuantitativo: medición de unidades Hounsfield en TAC, valores SUV en PET                               | PERJUDICIAL — altera la información cuantitativa |
| Detección de microcalcificaciones en mamografía                                                                    | PERJUDICIAL — los umbrales fijos de Canny pueden suprimir señales sutiles |
| Mediciones radiómicas o de textura                                                                                 | PERJUDICIAL — la ecualización destruye las estadísticas de intensidad originales |

### 6.3 Dificultades encontradas y la importancia de la ayuda de Python para el análisis de datos médicos

**Dificultades encontradas durante el desarrollo:**

1. **Heterogeneidad del dataset:** los archivos provenían de varios estudios y modalidades. Había archivos `.dcm`, `.jpg` y `.png` mezclados en las mismas carpetas, además de DICOMs con diferentes profundidades de bits (12, 16) y dimensiones (2D simples y volúmenes 3D multi-frame de _rsfMRI_).
2. **Tags ausentes por anonimización:** algunos archivos no incluían `StudyDescription` u otros tags.
3. **Imágenes sin `pixel_array`:** existen modalidades DICOM que no transportan píxeles. El acceso a `dataset.pixel_array` debía protegerse con `try/except`.
4. **Normalización antes de OpenCV:** los DICOMs vienen típicamente en `uint16` o más bits. OpenCV requiere `uint8`.
5. **Volúmenes 3D:** las resonancias _rsfMRI_ (PPMI) son multi-frame. Para no descartarlas, el programa toma la rebanada media del volumen al guardar el PNG, pero usa todo el volumen al calcular la intensidad promedio.

**Importancia de las herramientas de Python para el análisis de datos médicos:**

- **`pydicom`** abstrae la complejidad del estándar DICOM y permite acceder a cualquier tag como un atributo de Python. Sin esto habría que parsear manualmente la cabecera DICOM, que tiene cientos de tags definidos en el estándar.
- **`numpy`** nos entrega los píxeles como un arreglo sobre el que se pueden aplicar operaciones de vectores en milisegundos. Es la base sobre la que todo el ecosistema científico está construido.
- **`pandas`** convierte la información clínica en una _tabla_ consultable y exportable a CSV/Excel/SQL, abriendo la puerta a análisis estadísticos posteriores.
- **`OpenCV`** nos ofrece más de 500 funciones de visión por computador altamente optimizadas. Es la librería de referencia para preprocesamiento de imágenes médicas.

En conjunto, Python nos permite cubrir todo el flujo de nuestro procesamiento, ya sea desde leer un archivo DICOM hasta entrenar un modelo de _deep learning_ que detecte patologías. Todo con un solo lenguaje y un sistema de librerías.

---

## 7. Referencias

- DICOM Standard. _Digital Imaging and Communications in Medicine_. NEMA. <https://www.dicomstandard.org/>
- HL7 International. _Health Level Seven Standards_. <https://www.hl7.org/>
- _pydicom_ documentation. <https://pydicom.github.io/pydicom/>
- _OpenCV_ documentation. <https://docs.opencv.org/>
- Canny, J. (1986). _A Computational Approach to Edge Detection._ IEEE Transactions on PAMI, 8(6), 679–698.
- Kaggle. _MRI DICOM Scans dataset._
