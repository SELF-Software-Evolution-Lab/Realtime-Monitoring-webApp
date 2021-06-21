import time
import paho.mqtt.client as mqtt
from random import uniform

broker_address = "localhost"
broker_port = 8080
client = mqtt.Client()
client.connect(broker_address. broker_port)
topic = "temperature/Sogamoso/id.alfonso"

while True:
    value = round(uniform(1, 10),1)
    payload = "{\"value\":" + str(value) + "}"
    client.publish(topic, payload)
    print("Monitored temperature: " + str(value))
    print(payload)
    time.sleep(1)