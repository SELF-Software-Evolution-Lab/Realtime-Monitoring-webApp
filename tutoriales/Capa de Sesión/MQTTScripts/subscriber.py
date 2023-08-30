from datetime import datetime

import ssl
import paho.mqtt.client as mqtt

# Cambie esta variable por la dirección IP pública de su broker MQTT
HOST = "3.237.70.42"
PORT = 8082

USER = "admin"  # Cambie esta variable por el usuario administrador de su broker MQTT
PASSWD = "admin1234"  # Cambie esta variable por la contraseña del usuario indicado en USER

client = mqtt.Client("subscriber-test")
client.tls_set(ca_certs='ca.crt',
               tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)

def on_message(client_msg: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(log_date, "Data received: \n", message._topic.decode(
        "utf-8"), message.payload.decode("utf-8"))
    pass


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed!")
    pass


def on_connect(client, userdata, flags, rc):
    print("Connection:", mqtt.connack_string(rc))
    client.subscribe("#", qos=1)
    pass


def on_disconnect(client, userdata, rc):
    print("Disconnected:", mqtt.connack_string(rc))
    pass


def on_log(client, userdata, level, buf):
    print("Log: ", buf)
    pass


client.username_pw_set(USER, PASSWD)
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_connect = on_connect
client.on_connect_fail = on_connect
client.on_disconnect = on_disconnect

client.connect(HOST, PORT, 60)
client.loop_forever()
