# Archivo para procesar los archivos DICOM
import os
import pydicom
from pydicom.errors import InvalidDicomError
import numpy as np
import pandas as pd
import cv2


class ProcesadorDICOM:
    # Lista de tags DICOM que se van a extraer de cada archivo.
    TAGS_DICOM = [
        "PatientID",            # Identificador del paciente
        "PatientName",          # Nombre del paciente
        "StudyInstanceUID",     # Identificador unico del estudio
        "StudyDescription",     # Descripcion del estudio
        "StudyDate",            # Fecha del estudio
        "Modality",             # Modalidad.
        "Rows",                 # Numero de filas de la imagen
        "Columns",              # Numero de columnas de la imagen
    ]

    # Constructor: recibe la ruta de entrada y la ruta de salida.
    def __init__(self, directorio_entrada, directorio_salida="results"):
        self.directorio_entrada = directorio_entrada
        self.directorio_salida = directorio_salida

        self.archivos_dicom = []     
        self.dataframe = None 

        # Definir las subcarpetas donde se guardaran las imagenes procesadas.
        self.dir_ecualizadas = os.path.join(self.directorio_salida, "ecualizadas")
        self.dir_bordes = os.path.join(self.directorio_salida, "bordes")

        # Crea las carpetas de salida si no existen (exist_ok evita errores cuando ya existen).
        os.makedirs(self.dir_ecualizadas, exist_ok=True)
        os.makedirs(self.dir_bordes, exist_ok=True)

    # Metodo que recorre el directorio de entrada y carga todos los DICOM validos.
    def cargar_archivos(self):
        self.archivos_dicom = []  # Reinicia la lista por si el metodo se llama mas de una vez.

        # Contadores para mostrar un resumen al final del proceso.
        total_revisados = 0
        total_validos = 0
        total_invalidos = 0

        # Recorrer el arbol de directorios para cargar los archivos DICOM.
        for ruta_actual, _, archivos in os.walk(self.directorio_entrada):
            for nombre_archivo in archivos:
                total_revisados += 1
                ruta_completa = os.path.join(ruta_actual, nombre_archivo)

                try:
                    # Se intenta leer el archivo como DICOM. force=False obliga a que tenga la
                    # cabecera DICOM, asi se descartan automaticamente archivos .jpg, .png o .txt.
                    dataset = pydicom.dcmread(ruta_completa, force=False)
                    self.archivos_dicom.append((ruta_completa, dataset))  # Se guarda para usar despues.
                    total_validos += 1

                except InvalidDicomError:
                    total_invalidos += 1  # Archivos que NO son DICOM (jpg, png, txt, etc.).
                except Exception as error:
                    # Cualquier otro error, ya sea archivo corrupto, ilegible o dañado.
                    total_invalidos += 1
                    print("Error inesperado en " + nombre_archivo + ": " + str(error))

        # Imprime el resumen para que el usuario sepa cuantos archivos quedaron.
        print("\n--- Resumen de la carga ---")
        print("Archivos revisados:  " + str(total_revisados))
        print("Archivos DICOM:      " + str(total_validos))
        print("Archivos descartados:" + str(total_invalidos))

        return self.archivos_dicom

    # Metodo que extrae los metadatos de cada DICOM y los organiza en un DataFrame usando   pandas.
    def extraer_metadatos(self):
        registros = []  # Lista para guardar los diccionarios de los archivos.

        # Recorrer cada archivo cargado previamente.
        for ruta, dataset in self.archivos_dicom:
            # Cada fila empieza con el nombre del archivo de origen.
            fila = {"ArchivoOrigen": os.path.basename(ruta)}

            # Recorrer cada tag definido y extrae su valor.
            for tag in self.TAGS_DICOM:

                valor = getattr(dataset, tag, None)

                if valor is not None:
                    valor = str(valor)

                fila[tag] = valor

            registros.append(fila)

        # Crear el DataFrame final con todos los registros recogidos.
        self.dataframe = pd.DataFrame(registros)

        # Mostrar una vista previa de las primeras filas del DataFrame para verificar la estructura.
        print("\n--- DataFrame de datos ---")
        print("Numero total de filas: " + str(len(self.dataframe)))
        print(self.dataframe.head())

        return self.dataframe

    # Metodo para calcular la intensidad promedio de cada imagen.
    def calcular_intensidad(self):
        promedios = []

        # Recorrer   cada dataset en el mismo orden del DataFrame para mantener la correspondencia.
        for _, dataset in self.archivos_dicom:
            try:

                array_pixeles = dataset.pixel_array
                intensidad = float(np.mean(array_pixeles))

            except Exception:
                intensidad = np.nan

            promedios.append(intensidad)

        # Agregar la nueva columna al DataFrame ya construido.
        self.dataframe["IntensidadPromedio"] = promedios

        print("\n--- Intensidad promedio calculada ---")
        print("Imagenes con intensidad válida: " + str(self.dataframe['IntensidadPromedio'].notna().sum()))

        return self.dataframe

    # Funcion principal de preprocesamiento.
    def procesar_imagenes(self, umbral_bajo=50, umbral_alto=150):
        total_procesadas = 0
        total_omitidas = 0

        for indice, (ruta, dataset) in enumerate(self.archivos_dicom):
            nombre_base = os.path.splitext(os.path.basename(ruta))[0]
            try:
                array_pixeles = dataset.pixel_array
            except Exception as error:
                total_omitidas += 1
                modalidad = getattr(dataset, "Modality", "desconocida")
                print("Omitido (sin pixel_array) [" + str(modalidad) + "]: " + nombre_base + " -> " + str(error))
                continue

            # Manejo de imagenes multi-frame
            if array_pixeles.ndim == 3:
                indice_medio = array_pixeles.shape[0] // 2
                imagen_2d = array_pixeles[indice_medio]
            elif array_pixeles.ndim == 2:
                imagen_2d = array_pixeles  # Imagen 2D normal, se usa tal cual.
            else:
                # 4D u otros formatos exoticos no se soportan y se descartan.
                total_omitidas += 1
                print("Omitido (dimension no soportada): " + nombre_base)
                continue

            imagen_normalizada = cv2.normalize(imagen_2d, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            imagen_normalizada = imagen_normalizada.astype(np.uint8)

            imagen_ecualizada = cv2.equalizeHist(imagen_normalizada)

            imagen_bordes = cv2.Canny(imagen_ecualizada, umbral_bajo, umbral_alto)

            sufijo = str(indice).zfill(4) + "_" + nombre_base
            ruta_ecu = os.path.join(self.dir_ecualizadas, sufijo + "_eq.png")
            ruta_bor = os.path.join(self.dir_bordes, sufijo + "_canny.png")

            cv2.imwrite(ruta_ecu, imagen_ecualizada) 
            cv2.imwrite(ruta_bor, imagen_bordes)    

            total_procesadas += 1

        print("\n--- Procesamiento OpenCV ---")
        print("Imagenes procesadas:" + str(total_procesadas))
        print("Imagenes omitidas:  " + str(total_omitidas))

        return total_procesadas

    # Función para guardar el DataFrame final en un archivo CSV.
    def guardar_csv(self, nombre_archivo="metadatos.csv"):
        if self.dataframe is None:
            print("No hay DataFrame para guardar. Ejecute extraer_metadatos() primero.")
            return

        ruta_csv = os.path.join(self.directorio_salida, nombre_archivo)
        self.dataframe.to_csv(ruta_csv, index=False, encoding="utf-8")

        print("\nCSV guardado en: " + ruta_csv)
        return ruta_csv

# Hecho por: Sofia Cadavid Castro y Gabriela Sanin Vera