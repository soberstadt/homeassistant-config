I have a series of ESP8266 boards that serve as sensors around the house. Here there are and what they do:

## mqtt_arrow_1

Motion sensor in the 'sitting room'. Running MongooseOS. [Source](motion.js)

## mqtt_arrow_2

Weather and light sensor in the living room. Running MongooseOS. [Source](climate.js)

## mqtt_arrow_3

Garage door sensor. Running Arduino firmware. [Source](ultrasonic_mqtt.ino)

## mqtt_arrow_4

Motion sensor in the living room. Running esphomelib. [Source](mqtt_arrow_4.yaml)

## mqtt_arrow_5

Not yet integrated to HA. Intended to serve as a house lightswitch in the bedroom. Running esphomelib. [Source](mqtt_arrow_5.yaml)
