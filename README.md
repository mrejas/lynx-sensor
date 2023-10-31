# IoT Open Lynx Native Sensor

IoT Open Lynx WiFi sensor based on Raspberry Pi Pico. Even though this might
evolve to some useful sensor later on it is now to be seen as a POC that works.
The AIR sensor have been in use for some time when this is pushed and does
indeed work well.

## Description

The Raspberry Pi Pico is a capable microcontroller with plenty of I/O. This
software on a Pico W (WiFi) implements a couple of sensors.

## Integration to IoT Open

The sensor creates a device and functions in IoT Open that works right out of
the box. No gateway, no integration is needed. It is really easy to deploy.
That is the main advantage of this sensor, that it is so integrated to a
horizontal platform.

## Dual mode

The sensor can connect either directly to an IoT Open backend or to a local IoT
Open Edge Client.

## Configuration current

You need to add a config file to the Pico. See the exampel config file in the
code.

## Configuraton planned

Power on the sensor (3-5V) while pressing the button (or short Pin X and Y).
The Pico boots as an Access Point with an open WiFi netword called "LynxRules"
without password. The Pico has address 192.168.1.1 you set any address on the
192.168.1.0 network on the computer configuring the Pico. You need the
following data.

- SSID of the network the Pico should connect to
- PASSWORD to the network the Pico should connect to
- IoT Open API URL to the IoT Open instance, e.g. lynx.iotopen.se
- Mqtt broker and password
- API-Key from IoT Open
- ClientId from IoT Open

## Planned functionality

- Web configurator as described above
- Local http-api
- 
