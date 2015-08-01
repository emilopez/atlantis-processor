# atlantis-processor
App para detetección de Zonas Inundadas 
Autor: Atlantis Group

Módulo :loadLandsat.py
----------------------------
Descripción: Módulo para crear shapefile de cuerpos de agua desde una imagen Landsat 8

----------------------------
Cómo usar: prompt$ python loadLandsat.py <source_directory> <output_directory>

dónde 

\* <source_directory>: Es el path absoluto al directorio que contiene los tifs correspondientes a una imagen landsat.
Dicho directorio debe contener los 11 tifs correspondientes a las bandas del satélite junto con el archivo de metadatos.

\* <output_directory> : Directorio de salida de la aplicación.

----------------------------
Requisitos:

\* python 2.7

\* Grass GIs 7.x

\* Django 1.8

Además: Crear location <loc> en Grass Gis y mapset <map> con PROJ EPSG 4326 (leer desde alguna banda de Landsat)
		Agregar los nombres <loc> y <map> al script en líneas 29 y 30
