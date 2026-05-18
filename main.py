# Archivo principal del taller
import os
from procesador_dicom import ProcesadorDICOM  # Importa la clase para el procesamiento de los archivos.


def main():
    # Configurar las rutas de la carpeta de entrada de datos y de salida para los resultados.
    directorio_entrada = "data" 
    directorio_salida = "results"   

    # Crear una instancia del procesador con las rutas definidas.
    procesador = ProcesadorDICOM(directorio_entrada, directorio_salida)

    # Carga todos los archivos DICOM del directorio.
    print("=================================================")
    print("Cargando archivos DICOM desde '" + directorio_entrada + "'")
    print("=================================================")
    procesador.cargar_archivos()

    # Extraer los metadatos de cada DICOM y los organiza en un DataFrame.
    print("\n" + "=================================================")
    print("Extrayendo metadatos")
    print("=================================================")
    procesador.extraer_metadatos()

    # Calcula la intensidad promedio de cada imagen usando NumPy.
    print("\n" + "=================================================")
    print("Calculando intensidad promedio con NumPy")
    print("=================================================")
    procesador.calcular_intensidad()

    # Aplica el preprocesamiento con OpenCV que son normalizacion, ecualizacion y Canny.
    print("\n" + "=================================================")
    print("Procesando imagenes con OpenCV")
    print("=================================================")
    procesador.procesar_imagenes(umbral_bajo=50, umbral_alto=150)

    # Guarda el DataFrame final en un archivo CSV dentro de la carpeta de resultados.
    print("\n" + "=================================================")
    print("Guardando resultados")
    print("=================================================")
    procesador.guardar_csv("metadatos.csv")

    # Mensaje final indicando la ruta donde quedaron los resultados.
    ruta_absoluta = os.path.abspath(directorio_salida)
    print("\nProceso terminado. Revisa los resultados en: " + ruta_absoluta)


# Ejecutar main() cuando el archivo se corre directamente.
if __name__ == "__main__":
    main()

# Hecho por: Sofia Cadavid Castro y Gabriela Sanin Vera