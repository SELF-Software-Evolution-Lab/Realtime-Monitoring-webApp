from django.contrib import admin
from django.urls import path, include

# from . import mqtt
from . import utils

# Función que registra usuarios en la base de datos. Los datos los toma del archivo users.pwd
# que está en la carpeta raiz del proyecto.
# utils.register_users()

# Las siguientes 2 funciones se encargan de crear y actualizar el archivo CSV para descarga desde la página web
# No descomentar. Genera el archivo de todos los registros a la fecha. No corre con GUnicorn, se debe correr con python mnage.py runserver. Toma tiempo: para 200k datos tomó aprox. 10 min.
# utils.writeDataCSVFile()

# Actualiza el archivo creado con la función anterior. Este ejecuta un cron cada 30 min para la actualización del archivo.
# utils.updateCSVFile()

# Función que carga a la base de datos el CSV generado por las funciones anteriores.
# utils.loadCSV()

# Si se quieren generar datos de prueba, descomentar la siguiente función.
#
# utils.generateMockData()

# La siguiente línea se encarga de iniciar el proceso de MQTT y escuchar los mensajes.
# Descomentar para almacenar y registrar los mensajes que se publiquen desde las estaciones.
# mqtt.client.loop_start()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("realtimeGraph.urls")),
]
