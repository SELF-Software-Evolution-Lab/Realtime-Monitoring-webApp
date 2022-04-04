import ssl

from itsdangerous import json
import paho.mqtt.client as mqtt
from random import uniform
import time
import argparse

parser = argparse.ArgumentParser(description='IOT Sensor Emulator')
parser.add_argument("--host", type=str,
                    default="iotlab.virtual.uniandes.edu.co", help="MQTT Host")
# parser.add_argument("--user", type=str, required=True, help="MQTT User")
# parser.add_argument("--passwd", type=str, required=True, help="MQTT Password")
# parser.add_argument("--city", type=str, required=True, help="MQTT City")

args = parser.parse_args()

client = mqtt.Client("ID")


# def on_publish(client, userdata, result):
#     print("Data published: \n", client, userdata, result)
#     pass


def on_message(client, userdata, message):
    print("Data received: \n", client, userdata, message)
    pass


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: \n", client, userdata, mid, granted_qos)
    pass


def on_connect(client, userdata, flags, rc):
    print("Connected: \n", client, userdata, flags, rc)
    client.subscribe("#", qos=1)
    pass


def on_disconnect(client, userdata, rc):
    print("Disconnected: \n", client, userdata, rc)
    pass


def on_log(client, userdata, level, buf):
    print("Log: \n", client, userdata, level, buf)
    pass


client.tls_set(ca_certs='ca.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
print("TLS Done")
# client.username_pw_set(args.user, args.passwd)
# client.on_publish = on_publish
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_connect = on_connect
# client.on_connect_fail = on_connect
# client.on_disconnect = on_disconnect
client.on_log = on_log

client.connect(args.host, 8082, 60)
client.loop_forever()

# client.subscribe("#", 1)
