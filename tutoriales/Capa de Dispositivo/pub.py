import ssl

from itsdangerous import json
import paho.mqtt.client as mqtt
from random import uniform
import time

client = mqtt.Client()

usuario = "ja.avelino"
passwd = "monitoriaIOT2021"


def on_publish(client, userdata, result):
    print("Data published: \n", client, userdata, result)
    pass


client.tls_set(ca_certs='ca.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
client.username_pw_set(usuario, passwd)
client.on_publish = on_publish
client.connect("iotlab.virtual.uniandes.edu.co", 8082, 60)


while True:
    topic = "temperatura/cajica/" + usuario
    value = float(round(uniform(10, 30), 1))
    value = json.dumps({"value": value})
    result = client.publish(topic, value)
    print(topic + ": " + value)
    time.sleep(2)
