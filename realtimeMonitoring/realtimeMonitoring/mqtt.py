import paho.mqtt.client as mqtt
import json
from realtimeGraph.views import get_or_create_user, get_or_create_location, get_or_create_sensor, create_sensorData

broker_address = "localhost"
broker_port = 8080
topic = "#"

def on_message(client, userdata, message):
 payload = message.payload.decode("utf-8")
 payloadJson = json.loads(payload)
 print("Message=", payloadJson)
 topic = message.topic.split('/')
 print(topic)
 user = topic[2]
 location = topic[1]
 variable = topic[0]
 user_obj = get_or_create_user(user)
 location_obj = get_or_create_location(location)
 sensor_obj = get_or_create_sensor(variable, user_obj, location_obj)
 create_sensorData(sensor_obj, payloadJson["value"])
 #variable = get_variable(topic[2])
 #create_measurement_object("temperature", payloadJson["value"])

print("MQTT Start")
client = mqtt.Client('')
client.on_message = on_message
client.connect(broker_address, broker_port, 60)
client.subscribe(topic)