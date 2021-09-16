import paho.mqtt.client as mqtt
import json
import ssl
import traceback
from realtimeGraph.views import get_or_create_measurement, get_or_create_user, get_or_create_city, get_or_create_station, create_data

broker_address = "iotlab.virtual.uniandes.edu.co"
broker_port = 8082
topic = "#"


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        payloadJson = json.loads(payload)
        print("Message=", payloadJson)
        topic = message.topic.split('/')
        print(topic)
        user = topic[2]
        location = topic[1]
        variable = topic[0]
        user_obj = get_or_create_user(user)
        location_obj = get_or_create_city(location)
        unit = 'Celsius' if str(variable).lower() == 'temperatura' else '% MC'
        variable_obj = get_or_create_measurement(variable, unit)
        sensor_obj = get_or_create_station(user_obj, location_obj)
        create_data(payloadJson["value"], variable_obj, sensor_obj)
        #variable = get_variable(topic[2])
        #create_measurement_object("temperature", payloadJson["value"])
    except Exception as e:
        print('Ocurrió un error procesando el paquete MQTT', e)
        traceback.print_exc()


print("MQTT Start")
client = mqtt.Client('')
client.on_message = on_message
client.tls_set(ca_certs='/home/profesor/ca-prod.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
client.username_pw_set('uniandes', '*uniandesIOT2021!')
client.connect(broker_address, broker_port, 60)
client.subscribe(topic)
