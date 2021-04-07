#include <ESP8266WiFi.h>
#include <WiFiClient.h> 
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>


#include <SDS011.h>
#include "DHTesp.h"
#include "Adafruit_CCS811.h"

Adafruit_CCS811 ccs;
DHTesp dht;
SDS011 sds;

//////IoT-SNN-2
const char *ssid = "IoT-SNN-2";
const char *password = "mnlab1022";

//const char *ssid = "T234_2.4G";  
//const char *password = "choi1022";
//const char *host = "143.248.179.113/getdata.php";

//---------------- global getting each wemos d1 mini ------------------
int ID_and_ip = 47;
//---------------------------------------------------------------------

float refer_p25, refer_p10;
int p10, p25;
float h, t;
int co2, tvoc;
int error;

unsigned int period = 10000;//ms
unsigned int ref_period = 20000;

unsigned long m_time = 0;

void setup() {
  Serial.begin(115200);
  
  // -------------------- wifi setup --------------------
  delay(1000);
  WiFi.mode(WIFI_OFF);        //Prevents reconnection issue (taking too long to connect)
  delay(1000);
  WiFi.mode(WIFI_STA);        //This line hides the viewing of ESP as wifi hotspot
  IPAddress ip(192, 168, 0, ID_and_ip);
  IPAddress gateway(192, 168, 0, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, password);     //Connect to your WiFi router
  Serial.println("");

  Serial.print("Connecting");
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  //If connection successful show IP address in serial monitor
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());  //IP address assigned to your ESP

  // -------------------- wifi setup --------------------
  
  // -------------------- sensor setup --------------------
  // sds011 setup / D3핀(RX)와 SDS011 TX 핀 연결 / 4핀(TX)핀 사용 안함
  sds.begin(D3, D4);
  
  // DHT22 setup  
  dht.setup(D5, DHTesp::DHT22); // D5핀 온도 센서 사용
  
  // CCS811 setup D1핀 SCL, D2핀 SDA
//  if (!ccs.begin()) {
//    Serial.println("Failed to start sensor! Please check your wiring.");
//    while (1);
//  }
//  while (!ccs.available());   //calibrate temperature sensor
//  float temp = ccs.calculateTemperature();
//  ccs.setTempOffset(temp - 25.0);
  // -------------------------------------------------------------

  
  
}

void loop() {
  
  m_time = millis();
  // -------------------- measure the sensor data --------------------
  error = sds.read(&refer_p25, &refer_p10);
  if (! error) {
    p25 = int(refer_p25);
    p10 = int(refer_p10);
  }
  h = dht.getHumidity();
  t = dht.getTemperature();

//  if (ccs.available()) {
//    float temp = ccs.calculateTemperature();
//    ccs.setTempOffset(temp - 25.0);
//    if (!ccs.readData()) {
//      co2 = ccs.geteCO2();
//      tvoc = ccs.getTVOC();
//    }
//    else {
//      Serial.println("ERROR!");
//      while (1);
//    }
//  }
  Serial.print(t);
  Serial.print("\t");
  Serial.print(h);
  Serial.print("\t");
  Serial.print(p25);
  Serial.print("\t");
  Serial.print(p10);
  Serial.print("\t");
//  Serial.print(refer_p25);
//  Serial.print("\t");
//  Serial.print(refer_p10);
//  Serial.print("\t");
//  Serial.print(co2);
//  Serial.print("\t");
//  Serial.print(tvoc);
//  Serial.println();
  // ----------------------------------------------------------------------

  // -------------------- Send Http request to server --------------------
  HTTPClient http;    //Declare object of class HTTPClient
  String getData, Link;
  getData ="?id="+ String(ID_and_ip) +"&temp=" + String(t)+ "&humi="+ String(h)
  + "&dust2_5_1=" + String(p25)+ "&dust10_0_1="+ String(p10);
//  + "&co2_1=" + String(co2) + "&tvoc_1=" + String(tvoc);  //Note "?" added at front
  Link = "http://192.168.0.70:8090/getdata" +getData;

  
//  getData = "?rpi_id=" + String(ID_and_ip) 
//  + "&temp_1=" + String(t)+ "&humi_1="+ String(h)
//  + "&dust2_5_1=" + String(p25)+ "&dust10_0_1="+ String(p10)
//  + "&co2_1=" + String(co2) + "&tvoc_1=" + String(tvoc);  //Note "?" added at front
//  Link = "http://143.248.179.113/getdata.php" + getData;
//  Serial.println(Link);
  http.begin(Link);     //Specify request destination
  
  int httpCode = http.GET();            //Send the request
  String payload = http.getString();    //Get the response payload
  
  Serial.println(httpCode);   //Print HTTP return code
  //Print request response payload
//  Serial.print("Set sensing period to ");
//  Serial.print(payload);
//  Serial.println(" ms");

  if (httpCode == 200){
    period = payload.toInt();
  }
  else {
    period = ref_period;
  }
  Serial.print("Set sensing period to ");
  Serial.print(String(payload));
  Serial.println(" ms");
//  Serial.println(String(period));

  http.end();  //Close connection
  m_time = millis() - m_time;
  delay(period-m_time);
}
