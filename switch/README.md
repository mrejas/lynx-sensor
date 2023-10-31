# IoT Open Lynx Native Sensor
IoT Open Lynx WiFi sensor based on Raspberry Pi Pico

## Description
The Raspberry Pi Pico is a capable microcontroller with plenty of I/O. This software on a Pico W (WiFi) implements a simple switch on GPIO16 with a controller on GPIO17. When GPIO17 goes hight the GPIO16 tggles.

## Integration to IoT Open
The sensor creates a device and functions in IoT Open that works right out of the box. No gateway, no integration is needed. It is really easy to deploy.

## Configuraton
Power on the sensor (3-5V) while pressing the button (or short Pin X and Y). The Pico boots as an Access Point with an open WiFi netword called "LynxRules" without password. The Pico has address 192.168.1.1 you set any address on the 192.168.1.0 network on the computer configuring the Pico. You need the following data.

- SSID of the network the Pico should connect to
- PASSWORD to the network the Pico should connect to
- IoT Open URL to the IoT Open instance, e.g. lynx.iotopen.se
- API-Key from IoT Open
- ClientId from IoT Open

## Control from IoT Open

### Via the GUI

### Via MQTT

### Via REST-API
