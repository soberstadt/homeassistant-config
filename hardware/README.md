I have a series of ESP8266 boards that serve as sensors around the house. Here there are and what they do:

## mqtt_arrow_1

Room | Firmware | source | purpose | hardware
--- | --- | --- | --- | ---
Sitting Room | MongooseOS | [Source](motion.js) | Motion sensor | NodeMCU

## mqtt_arrow_2

Room | Firmware | source | purpose | hardware
--- | --- | --- | --- | ---
Living Room | MongooseOS | [Source](climate.js) | Climate and Light sensor | D1 Mini

## mqtt_arrow_3

Room | Firmware | source | purpose | hardware
--- | --- | --- | --- | ---
Garage | Arduino | [Source](ultrasonic_mqtt.ino) | Garage door sensor

## mqtt_arrow_4

Room | Firmware | source | purpose | hardware
--- | --- | --- | --- | ---
Living Room | esphomelib | [Source](mqtt_arrow_4.yaml) | Motion sensor | NodeMCU

## mqtt_arrow_5

Room | Firmware | source | purpose | hardware
--- | --- | --- | --- | ---
Not integrated | esphomelib | [Source](mqtt_arrow_5.yaml) | House light switch button | D1 Mini