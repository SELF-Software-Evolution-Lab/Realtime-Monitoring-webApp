#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>
#include <PubSubClient.h>
#include "DHT.h"
#define DHTTYPE DHT11 // DHT 11

#define dht_dpin 4
DHT dht(dht_dpin, DHTTYPE);

#include "secrets.h"

//Conexión a Wifi
//Nombre de la red Wifi
const char ssid[] = "wifi-name";
//Contraseña de la red Wifi
const char pass[] = "wifi-password";

//Usuario uniandes sin @uniandes.edu.co
#define HOSTNAME "nodeMCU-hostname"

//Conexión a Mosquitto
const char MQTT_HOST[] = "iotlab.virtual.uniandes.edu.co";
const int MQTT_PORT = 8082;
//Usuario uniandes sin @uniandes.edu.co
const char MQTT_USER[] = "mosquitto-user";
//Contraseña de MQTT que recibió por correo
const char MQTT_PASS[] = "mosquitto-password";
const char MQTT_SUB_TOPIC[] = HOSTNAME "/";
//Tópico al que se enviarán los datos de humedad
const char MQTT_PUB_TOPIC1[] = "humedad/ciudad/" HOSTNAME;
//Tópico al que se enviarán los datos de temperatura
const char MQTT_PUB_TOPIC2[] = "temperatura/ciudad/" HOSTNAME;

//////////////////////////////////////////////////////

#if (defined(CHECK_PUB_KEY) and defined(CHECK_CA_ROOT)) or (defined(CHECK_PUB_KEY) and defined(CHECK_FINGERPRINT)) or (defined(CHECK_FINGERPRINT) and defined(CHECK_CA_ROOT)) or (defined(CHECK_PUB_KEY) and defined(CHECK_CA_ROOT) and defined(CHECK_FINGERPRINT))
  #error "cant have both CHECK_CA_ROOT and CHECK_PUB_KEY enabled"
#endif

BearSSL::WiFiClientSecure net;
PubSubClient client(net);

time_t now;
unsigned long lastMillis = 0;

//Función que conecta el node a través del protocolo MQTT
//Emplea los datos de usuario y contraseña definidos en MQTT_USER y MQTT_PASS para la conexión
void mqtt_connect()
{
  //Intenta realizar la conexión indefinidamente hasta que lo logre
  while (!client.connected()) {
    Serial.print("Time: ");
    Serial.print(ctime(&now));
    Serial.print("MQTT connecting ... ");
    if (client.connect(HOSTNAME, MQTT_USER, MQTT_PASS)) {
      Serial.println("connected.");
    } else {
      Serial.println("Problema con la conexión, revise los valores de las constantes MQTT");
      Serial.print("Código de error = ");
      Serial.println(client.state());
      if ( client.state() == MQTT_CONNECT_UNAUTHORIZED ) {
        ESP.deepSleep(0);
      }
      /* Espera 5 segundos antes de volver a intentar */
      delay(5000);
    }
  }
}

void receivedCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Received [");
  Serial.print(topic);
  Serial.print("]: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
}

//Configura la conexión del node MCU a Wifi y a Mosquitto
void setup()
{
  Serial.begin(115200);
  Serial.println();
  Serial.println();
  Serial.print("Attempting to connect to SSID: ");
  Serial.print(ssid);
  WiFi.hostname(HOSTNAME);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  //Intenta conectarse con los valores de las constantes ssid y pass a la red Wifi
  //Si la conexión falla el node se dormirá hasta que lo resetee
  while (WiFi.status() != WL_CONNECTED)
  {
    if ( WiFi.status() == WL_NO_SSID_AVAIL || WiFi.status() == WL_WRONG_PASSWORD ) {
      Serial.print("\nProblema con la conexión, revise los valores de las constantes ssid y pass");
      ESP.deepSleep(0);
    } else if ( WiFi.status() == WL_CONNECT_FAILED ) {
      Serial.print("\nNo se ha logrado conectar con la red, resetee el node y vuelva a intentar");
      ESP.deepSleep(0);
    }
    Serial.print(".");
    delay(1000);
  }
  Serial.println("connected!");

  //Sincroniza la hora del dispositivo con el servidor SNTP (Simple Network Time Protocol)
  Serial.print("Setting time using SNTP");
  configTime(-5 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  now = time(nullptr);
  while (now < 1510592825) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println("done!");
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  //Una vez obtiene la hora, imprime en el monitor el tiempo actual
  Serial.print("Current time: ");
  Serial.print(asctime(&timeinfo));

  #ifdef CHECK_CA_ROOT
    BearSSL::X509List cert(digicert);
    net.setTrustAnchors(&cert);
  #endif
  #ifdef CHECK_PUB_KEY
    BearSSL::PublicKey key(pubkey);
    net.setKnownKey(&key);
  #endif
  #ifdef CHECK_FINGERPRINT
    net.setFingerprint(fp);
  #endif
  #if (!defined(CHECK_PUB_KEY) and !defined(CHECK_CA_ROOT) and !defined(CHECK_FINGERPRINT))
    net.setInsecure();
  #endif

  //Llama a funciones de la librería PubSubClient para configurar la conexión con Mosquitto
  client.setServer(MQTT_HOST, MQTT_PORT);
  client.setCallback(receivedCallback);
  //Llama a la función de este programa que realiza la conexión con Mosquitto
  mqtt_connect();
}

//Función loop que se ejecuta indefinidamente repitiendo el código a su interior
//Cada vez que se ejecuta toma nuevos datos de la lectura del sensor
void loop()
{
  //Revisa que la conexión Wifi y MQTT siga activa
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.print("Checking wifi");
    while (WiFi.waitForConnectResult() != WL_CONNECTED)
    {
      WiFi.begin(ssid, pass);
      Serial.print(".");
      delay(10);
    }
    Serial.println("connected");
  }
  else
  {
    if (!client.connected())
    {
      mqtt_connect();
    }
    else
    {
      client.loop();
    }
  }

  now = time(nullptr);
  //Lee los datos del sensor
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  //Transforma la información a la notación JSON para poder enviar los datos 
  //El mensaje que se envía es de la forma {"value": x}, donde x es el valor de temperatura o humedad
  
  //JSON para humedad
  String json = "{\"value\": "+ String(h) + "}";
  char payload1[json.length()+1];
  json.toCharArray(payload1,json.length()+1);
  //JSON para temperatura
  json = "{\"value\": "+ String(t) + "}";
  char payload2[json.length()+1];
  json.toCharArray(payload2,json.length()+1);

  //Si los valores recolectados no son indefinidos, se envían a los tópicos correspondientes
  if ( !isnan(h) && !isnan(t) ) {
    //Publica en el tópico de la humedad
    client.publish(MQTT_PUB_TOPIC1, payload1, false);
    //Publica en el tópico de la temperatura
    client.publish(MQTT_PUB_TOPIC2, payload2, false);
  }

  //Imprime en el monitor serial la información recolectada
  Serial.print(MQTT_PUB_TOPIC1);
  Serial.print(" -> ");
  Serial.println(payload1);
  Serial.print(MQTT_PUB_TOPIC2);
  Serial.print(" -> ");
  Serial.println(payload2);
  /*Espera 5 segundos antes de volver a ejecutar la función loop*/
  delay(5000);
}
