#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>
#include <PubSubClient.h>
#include "DHT.h"
#define DHTTYPE DHT11 // DHT 11

#define dht_dpin 4
DHT dht(dht_dpin, DHTTYPE);

#include "secrets.h"

const char ssid[] = "wifi-name";
const char pass[] = "wifi-password";

#define HOSTNAME "nodeMCU-hostname"

const char MQTT_HOST[] = "iotlab.virtual.uniandes.edu.co";
const int MQTT_PORT = 8082;
const char MQTT_USER[] = "mosquitto-user"; // leave blank if no credentials used
const char MQTT_PASS[] = "mosquitto-password"; // leave blank if no credentials used
const char MQTT_SUB_TOPIC[] = HOSTNAME "/";
const char MQTT_PUB_TOPIC1[] = "moisture/city/" HOSTNAME;
const char MQTT_PUB_TOPIC2[] = "temperature/city/" HOSTNAME;

//////////////////////////////////////////////////////

#if (defined(CHECK_PUB_KEY) and defined(CHECK_CA_ROOT)) or (defined(CHECK_PUB_KEY) and defined(CHECK_FINGERPRINT)) or (defined(CHECK_FINGERPRINT) and defined(CHECK_CA_ROOT)) or (defined(CHECK_PUB_KEY) and defined(CHECK_CA_ROOT) and defined(CHECK_FINGERPRINT))
  #error "cant have both CHECK_CA_ROOT and CHECK_PUB_KEY enabled"
#endif

BearSSL::WiFiClientSecure net;
PubSubClient client(net);

time_t now;
unsigned long lastMillis = 0;

void mqtt_connect()
{
  while (!client.connected()) {
    Serial.print("Time: ");
    Serial.print(ctime(&now));
    Serial.print("MQTT connecting ... ");
    if (client.connect(HOSTNAME, MQTT_USER, MQTT_PASS)) {
      Serial.println("connected.");
      //client.subscribe(MQTT_SUB_TOPIC);
    } else {
      Serial.print("failed, status code =");
      Serial.print(client.state());
      Serial.println(". Try again in 5 seconds.");
      /* Wait 5 seconds before retrying */
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
  while (WiFi.status() != WL_CONNECTED)
  {
    if ( WiFi.status() == WL_NO_SSID_AVAIL ) {
      Serial.print("\nLa red WiFi no se ha encontrado, revise que haya escrito correctamente el nombre de la red en el valor de la constante ssid");
      ESP.deepSleep(0);
    } else if ( WiFi.status() == WL_WRONG_PASSWORD ) {
      Serial.print("\nLa contraseña ingresada no es correcta, revise que haya escrito correctamente la contraseña de la red en el valor de la constante pass");
      ESP.deepSleep(0);
    } else if ( WiFi.status() == WL_CONNECT_FAILED ) {
      Serial.print("\nNo se ha logrado conectar con la red, resetee el node y vuelva a intentar");
      ESP.deepSleep(0);
    }
    Serial.print(".");
    delay(1000);
  }
  Serial.println("connected!");

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

  client.setServer(MQTT_HOST, MQTT_PORT);
  client.setCallback(receivedCallback);
  mqtt_connect();
}

void loop()
{
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
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  String json = "{\"value\": "+ String(h) + "}";
  char payload1[json.length()+1];
  json.toCharArray(payload1,json.length()+1);
  json = "{\"value\": "+ String(t) + "}";
  char payload2[json.length()+1];
  json.toCharArray(payload2,json.length()+1);
  if ( !isnan(h) && !isnan(t) ) {
    client.publish(MQTT_PUB_TOPIC1, payload1, false);
    client.publish(MQTT_PUB_TOPIC2, payload2, false);
  }
  Serial.print(MQTT_PUB_TOPIC1);
  Serial.print(" -> ");
  Serial.println(payload1);
  Serial.print(MQTT_PUB_TOPIC2);
  Serial.print(" -> ");
  Serial.println(payload2); 
  delay(5000);
}
