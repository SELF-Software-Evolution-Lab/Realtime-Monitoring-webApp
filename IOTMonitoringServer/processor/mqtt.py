from datetime import datetime
from . import utils
import json
import os
import ssl
import paho.mqtt.client as mqtt

# Dirección del bróker MQTT
MQTT_HOST = "44.201.18.140"

# Puerto del bróker MQTT
MQTT_PORT = 8082

# Credenciales para conexión con el bróker MQTT
MQTT_USER = "admin"
MQTT_PASSWORD = "admin1234"

# Tópico a suscribir. '#' se refiere a todos los tópicos.
TOPIC = "#"

# Ubicación del archivo de certificado para conexión TLS con el bróker MQTT
CA_CRT_FILE = "ssl/ca.crt"
CA_CRT_PATH = os.path.join(os.path.dirname(__file__), CA_CRT_FILE)

# TODO Implementar logs


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    '''
    Función que se ejecuta cada que llega un mensaje al tópico.
    Recibe el mensaje con formato:
        {
            "variable1": mediciónVariable1,
            "variable2": mediciónVariable2
        }
    en un tópico con formato:
        pais/estado/ciudad/usuario
        ej: colombia/cundinamarca/cajica/ja.avelino
    Si el tópico tiene la forma de:
        pais/estado/ciudad/usuario/mensaje
    se salta el procesamiento pues el mensaje es para el dispositivo de medición.
    A partir de esos datos almacena la medición en el sistema.
    '''
    try:
        time = datetime.now()
        payload = message.payload.decode("utf-8")
        print("payload: " + payload)
        payloadJson = json.loads(payload)
        country, state, city, user, message = utils.get_topic_data(
            message.topic)

        if message is not None:
            return

        user_obj = utils.get_user(user)
        location_obj = utils.get_or_create_location(city, state, country)

        for measure in payloadJson:
            variable = measure
            unit = utils.get_units(str(variable).lower())
            variable_obj = utils.get_or_create_measurement(variable, unit)
            sensor_obj = utils.get_or_create_station(user_obj, location_obj)
            utils.create_data(
                float(payloadJson[measure]), sensor_obj, variable_obj, time)

    except Exception as e:
        print('Ocurrió un error procesando el paquete MQTT', e)


def on_connect(client, userdata, flags, rc):
    print("Suscribiendo al tópico: " + TOPIC)
    client.subscribe(TOPIC)


def on_disconnect(client: mqtt.Client, userdata, rc):
    '''
    Función que se ejecuta cuando se desconecta del broker.
    Intenta reconectar al bróker.
    '''
    print("Desconectado con mensaje:" + str(mqtt.connack_string(rc)))
    print("Reconectando...")
    client.reconnect()


print("Iniciando cliente MQTT...")
try:
    client = mqtt.Client(MQTT_USER)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    # Descomentar para usar TLS
    # client.tls_set(ca_certs=CA_CRT_PATH,
    #                tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT)
except Exception as e:
    print('Ocurrió un error al conectar con el bróker MQTT:', e)
