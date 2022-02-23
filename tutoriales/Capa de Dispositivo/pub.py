import ssl

from itsdangerous import json
import paho.mqtt.client as mqtt
from random import uniform
import time
import argparse

parser = argparse.ArgumentParser(description='IOT Sensor Emulator')
parser.add_argument("--host", type=str,
                    default="iotlab.virtual.uniandes.edu.co", help="MQTT Host")
parser.add_argument("--user", type=str, required=True, help="MQTT User")
parser.add_argument("--passwd", type=str, required=True, help="MQTT Password")
parser.add_argument("--city", type=str, required=True, help="MQTT City")

args = parser.parse_args()

client = mqtt.Client()


def on_publish(client, userdata, result):
    print("Data published: \n", client, userdata, result)
    pass


client.tls_set(ca_certs='ca.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
client.username_pw_set(args.user, args.passwd)
client.on_publish = on_publish
client.connect(args.host, 8082, 60)


while True:
    topic1 = "temperatura/{}/{}".format(args.city, args.user)
    topic2 = "humedad/{}/{}".format(args.city, args.user)
    value1 = float(round(uniform(10, 30), 1))
    value2 = float(round(uniform(50, 99), 1))
    value1 = json.dumps({"value": value1})
    value2 = json.dumps({"value": value2})
    result1 = client.publish(topic1, value1)
    result2 = client.publish(topic2, value2)
    print(topic1 + ": " + value1)
    print(topic2 + ": " + value2)
    time.sleep(2)
