from datetime import datetime
import paho.mqtt.client as mqtt
import time
import argparse
import ssl

parser = argparse.ArgumentParser(description='IOT Sensor Emulator')
parser.add_argument("--host", type=str,
                    default="iotlab.virtual.uniandes.edu.co", help="MQTT Host")
parser.add_argument("--port", type=int,
                    default=8082, help="MQTT Port")
parser.add_argument("--user", type=str, required=False, help="MQTT User")
parser.add_argument("--passwd", type=str, required=False, help="MQTT Password")
parser.add_argument("--topic", type=str, default="/",
                    required=False, help="MQTT Topic")

args = parser.parse_args()

client = mqtt.Client("Pub-test")
client.tls_set(ca_certs='ca.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)

def send_messages():
    while True:
        topic = args.topic
        message = "MQTT Test"
        res = client.publish(topic, message)
        log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(log_date, topic + ": " + message)
        print("\tMsg:", mqtt.connack_string(res[0]))
        time.sleep(2)


def on_publish(client, userdata, result):
    print("Publish successful!")
    pass


def on_connect(client, userdata, flags, rc):
    print("Connected: ", rc)
    pass


def on_error(client, userdata, rc):
    print("Connection failed!", rc)
    pass


def on_disconnect(client, userdata, rc):
    print("Disconnected!", mqtt.connack_string(rc))
    pass


def on_log(client, userdata, level, buf):
    print("Log: ", buf)
    pass


client.username_pw_set(args.user, args.passwd)
client.on_connect = on_connect
client.on_publish = on_publish
client.on_connect_fail = on_error
client.on_disconnect = on_disconnect
client.connect(args.host, args.port, 60)
send_messages()
