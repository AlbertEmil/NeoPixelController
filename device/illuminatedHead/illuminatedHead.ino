#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN             6
#define LED_COUNT           16
#define MAX_BRIGHTNESS      255
#define JSON_DOCUMENT_SIZE  256

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);
StaticJsonDocument<JSON_DOCUMENT_SIZE> doc;

// {
//     "red": 255,
//     "green": 255,
//     "blue": 255,
//     "white": 255,
//     "brightness": 255,
//     "setAsDefault": true
// }

void setup()
{
  strip.begin();      
  strip.show();       
  strip.setBrightness(MAX_BRIGHTNESS);
  
  Serial.begin(115200);
  while (!Serial) {
    continue;
  }
}


void updateLeds()
{
  // TODO: Improvement: Think about incomplete JSON objects with missing data
  
  uint8_t red = doc["red"];
  uint8_t green = doc["green"];
  uint8_t blue = doc["blue"];
  uint8_t white = doc["white"];
  uint8_t brightness = doc["brightness"];
  uint8_t setAsDefault = doc["setAsDefault"];
  
  Serial.print("Red: ");
  Serial.println(red);
  
  Serial.print("Green: ");
  Serial.println(green);
  
  Serial.print("Blue: ");
  Serial.println(blue);
  
  Serial.print("White: ");
  Serial.println(white);
  // Serial.println(brightness);

  uint32_t color = strip.Color(red, green, blue, white); 
  for (uint8_t i=0; i<LED_COUNT; i++)
  {
    strip.setPixelColor(i, color);
  }
    // setBrightness should only be called once in setup() and not used to adjust the brightness afterwards (https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library-use)
    // TODO: Feature: Think about setting the brightness by adjusting the color values (perform calculations on uC or in GUI? Use gamma corrected values to keep color ratios)
    // strip.setBrightness(brightness);
    strip.show();

    // TODO: Save as new default values if `setAsDefault` set to true
}


void loop()
{
  while(Serial.available())
  {
    // https://github.com/bblanchon/ArduinoJson/issues/862
    char nextChar = Serial.peek();
    if ( (nextChar == '\r') or (nextChar == '\n') )
    {
      Serial.read();
      Serial.println("Removing left over CR or LF");
      continue;
    };
    
    DeserializationError error = deserializeJson(doc, Serial);
    if (error)
    {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      continue;
    }

    updateLeds();

  };
  
}
