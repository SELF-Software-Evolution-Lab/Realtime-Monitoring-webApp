import paho.mqtt.client as mqtt
import json
import ssl
import traceback
from realtimeGraph.views import get_or_create_location, get_or_create_measurement, get_or_create_user, get_or_create_station, create_data
from django.utils import timezone

# Dirección del bróker MQTT
broker_address = "iotlab.virtual.uniandes.edu.co"
# Puerto del bróker MQTT
broker_port = 8082
# Tópico a suscribir. '#' se refiere a todos los tópicos.
topic = "#"

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
A partir de esos datos almacena la medición en el sistema.
'''
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        payloadJson = json.loads(payload)
        print("Message=", payloadJson)
        topic = message.topic.split('/')
        print(topic)
        user = topic[3]
        country = topic[0]
        state = topic[1]
        city = topic[2]
        if city == "ciudad":
            print("Se salta el registro por nombre incorrecto de ciudad")
            raise Exception("Ciudad incorrecta")
        user_obj = get_or_create_user(user)
        location_obj = get_or_create_location(city, state, country)
        for measure in payloadJson:
            variable = measure
            unit = '°C' if str(variable).lower() == 'temperatura' else '%'
            variable_obj = get_or_create_measurement(variable, unit)
            sensor_obj = get_or_create_station(user_obj, location_obj)
            create_data(payloadJson[measure], sensor_obj, variable_obj)
            
    except Exception as e:
        print('Ocurrió un error procesando el paquete MQTT', e)
        traceback.print_exc()


print("MQTT Start")
client = mqtt.Client('')
print("Time: ", timezone.now())
client.on_message = on_message
client.tls_set(ca_certs='/home/javos/ca.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
client.username_pw_set('uniandes', '*uniandesIOT2021!')
client.connect(broker_address, broker_port, 60)
client.subscribe(topic)
