from wifi_network import Network
import time
from machine import Pin, I2C, WDT
import machine
from umqtt.robust import MQTTClient
import ubinascii
import json
import ntptime
import utime
from lynx import Lynx
from led_utils import *
from bmp180 import BMP180
import adafruit_sgp30
from config import config

wdt = WDT(timeout=8000)  	# Watchdog must be fed every 8s,
                            # therefore the many wdt.feed() calls,
                            # We don't want it to get hungry.

#
# Parse all config parameters, taking mode into consideration.
#
installation_id = config['lynx']['installation_id']
lynx_api = config['lynx']['api']
lynx_api_key = config['lynx']['api_key']

if config['lynx']['mode'] == 'edge':
    client_id_prefix = ''
    mqtt_broker = config['mqtt']['broker']
    mqtt_password = config['mqtt']['password']
    mqtt_username = config['mqtt']['username']
    mqtt_port = 1883
    mqtt_ssl = False
else:
    client_id_prefix = str(config['lynx']['client_id']) + '/'
    mqtt_broker = config['lynx']['api']
    mqtt_password = config['lynx']['api_key']
    mqtt_username = 'rejas-wifi-sensor'
    mqtt_port = 8883
    mqtt_ssl = True    


mqtt_client_id = ubinascii.hexlify(machine.unique_id())

led = Pin('LED', Pin.OUT) # The LED is used for signaling to the user

net = Network(config['wlan'])
net.connect()
mac = net.mac # We use the MAC as identifier

wdt.feed()

ntptime.settime()

wdt.feed()

year, month, day, hour, mins, secs, weekday, yearday = time.localtime()   

led_blink(led, 3)

boot_time = time.time()

i2c = I2C(0, sda = Pin(4), scl = Pin(5), freq = 10000)

wdt.feed()

sgp = adafruit_sgp30.Adafruit_SGP30(i2c)
bmp = BMP180(i2c)

wdt.feed()

#
# Define all the topics needed
#
topic_write_base = 'set/rejaswifi/' + mac
topic_cmd_base = 'cmd/rejaswifi/' + mac

topic_read_temperature = 'obj/rejaswifi/' + mac + '/temperature'
topic_write_temperature_interval = topic_write_base + '/temperature/interval'
topic_read_temperature_interval = 'obj/rejaswifi/' + mac + '/temperature/interval'

topic_read_pressure = 'obj/rejaswifi/' + mac + '/pressure'
topic_write_pressure_interval = topic_write_base + '/pressure/interval'
topic_read_pressure_interval = 'obj/rejaswifi/' + mac + '/pressure/interval'

topic_read_eco2 = 'obj/rejaswifi/' + mac + '/eco2'
topic_write_eco2_interval = topic_write_base + '/eco2/interval'
topic_read_eco2_interval = 'obj/rejaswifi/' + mac + '/eco2/interval'

topic_read_tvoc = 'obj/rejaswifi/' + mac + '/tvoc'
topic_write_tvoc_interval = topic_write_base + '/tvoc/interval'
topic_read_tvoc_interval = 'obj/rejaswifi/' + mac + '/tvoc/interval'

topic_status = 'obj/rejaswifi/' + mac + '/alive'
topic_uptime = 'obj/rejaswifi/' + mac + '/uptime'
topic_cmd_ping = 'cmd/rejaswifi/' + mac + '/ping'
topic_evt_pong = 'evt/rejaswifi/' + mac + '/pong'

topic_cmd_get_temperature = 'cmd/rejaswifi/' + mac + '/temperature/get'
topic_cmd_get_pressure = 'cmd/rejaswifi/' + mac + '/pressure/get'
topic_cmd_get_tvoc = 'cmd/rejaswifi/' + mac + '/tvoc/get'
topic_cmd_get_eco2 = 'cmd/rejaswifi/' + mac + '/eco2/get'

def save_intervals():
    intervals = { "t":temperature_interval,
                  "p":pressure_interval,
                  "e":eco2_interval,
                  "t":tvoc_interval }
    try:
        with open('intervals.json', 'w') as f:
            json.dump(intervals, f)
        f.close()
    except:
        print("Error! Could not save")


def load_intervals():
    global temperature_interval, pressure_interval, eco2_interval, tvoc_interval
    try:
        with open('intervals.json', 'r') as f:
            intervals = json.load(f)
            temperature_interval = intervals["t"]
            pressure_interval = intervals["p"]
            eco2_interval = intervals["e"]
            tvoc_interval = intervals["t"]
        f.close()
    except:
        # Default is report once an hour
        temperature_interval = 3600
        pressure_interval = 3600
        eco2_interval = 3600
        tvoc_interval = 3600


# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global temperature_interval
    global pressure_interval
    global eco2_interval
    global tvoc_interval

    data = json.loads(msg);
    value = data['value'];
    if topic.decode() == client_id_prefix + topic_write_temperature_interval:
        temperature_interval = value
        client.publish(client_id_prefix + topic_read_temperature_interval, '{ "value":' + str(value) +  ', "timestamp": ' + str(time.time()) + ' }')
        save_intervals()
    if topic.decode() == client_id_prefix + topic_write_pressure_interval:
        pressure_interval = value
        client.publish(client_id_prefix + topic_read_pressure_interval, '{ "value":' + str(value) +  ', "timestamp": ' + str(time.time()) + ' }')
        save_intervals()
    if topic.decode() == client_id_prefix + topic_write_eco2_interval:
        eco2_interval = value
        client.publish(client_id_prefix + topic_read_eco2_interval, '{ "value":' + str(value) +  ', "timestamp": ' + str(time.time()) + ' }')
        save_intervals()
    if topic.decode() == client_id_prefix + topic_write_tvoc_interval:
        tvoc_interval = value
        client.publish(client_id_prefix + topic_read_tvoc_interval, '{ "value":' + str(value) +  ', "timestamp": ' + str(time.time()) + ' }')
        save_intervals()
    if topic.decode() == client_id_prefix + topic_cmd_get_temperature:
        temp = bmp.temperature
        client.publish(client_id_prefix + topic_read_temperature, '{ "value":' + str(temp) +  ', "timestamp": ' + str(time.time()) + ' }')

    if topic.decode() == client_id_prefix + topic_cmd_get_pressure:
        pressure = bmp.pressure
        client.publish(client_id_prefix + topic_read_pressure, '{ "value":' + str(pressure) +  ', "timestamp": ' + str(time.time()) + ' }')

    if topic.decode() == client_id_prefix + topic_cmd_get_eco2:
        co2eq, tvoc = sgp.iaq_measure()
        client.publish(client_id_prefix + topic_read_eco2, '{ "value":' + str(co2eq) +  ', "timestamp": ' + str(time.time()) + ' }')

    if topic.decode() == client_id_prefix + topic_cmd_get_tvoc:
        co2eq, tvoc = sgp.iaq_measure()
        client.publish(client_id_prefix + topic_read_tvoc, '{ "value":' + str(tvoc) +  ', "timestamp": ' + str(time.time()) + ' }')

    if topic.decode() == client_id_prefix + topic_cmd_ping:
        client.publish(client_id_prefix + topic_evt_pong, '{ "value":' + str(value) +  ', "timestamp": ' + str(time.time()) + ' }')



def mqtt_connect():
    client = MQTTClient(mqtt_client_id, mqtt_broker,
                        user=b'picosensor',
                        password=mqtt_password,
                        port=mqtt_port,
                        ssl=mqtt_ssl,
                        keepalive=30)
    client.set_callback(sub_cb)
    client.set_last_will(client_id_prefix + topic_status, '{"value": 0}')
    client.connect()
    client.subscribe(client_id_prefix + topic_write_base + '/#')
    client.subscribe(client_id_prefix + topic_cmd_base + '/#')
    client.publish(client_id_prefix + topic_status, '{"value": 1}')
    led_blink(led, 5)
    return client

def reconnect():
    time.sleep(5)
    machine.reset()

def create_lynx_objects():
    lynx = Lynx(lynx_api, installation_id, lynx_api_key)
    
    device = {
        "installation_id": installation_id,
        "type": "rejaswifi",
        "meta": {
            "name": "WiFi AIR: " + mac,
            "mac": mac
        }
    }
    
    device_id = lynx.create_device_if_needed(device)
    
    
    function_temperature = {
        "installation_id": installation_id,
        "type": 'temperature',
        "meta": {
            "device_id": str(device_id),
            "name": mac + " temperature",
            "topic_read": topic_read_temperature,
            "topic_read_interval": topic_read_temperature_interval,
            "topic_write_interval": topic_write_temperature_interval,
            "topic_cmd_get": topic_cmd_get_temperature,
            "format": "%0.1f °C"
        }
    }
    
    
    function_tvoc = {
        "installation_id": installation_id,
        "type": 'tvoc',
        "meta": {
            "device_id": str(device_id),
            "name": mac + " tvoc",
            "topic_read": topic_read_tvoc,
            "topic_read_interval": topic_read_tvoc_interval,
            "topic_write_interval": topic_write_tvoc_interval,
            "topic_cmd_get": topic_cmd_get_tvoc,
            "format": "%0.0f ppb"
        }
    }
    
    function_eco2 = {
        "installation_id": installation_id,
        "type": 'eco2',
        "meta": {
            "device_id": str(device_id),
            "name": mac + " eCO2",
            "topic_read": topic_read_eco2,
            "topic_read_interval": topic_read_eco2_interval,
            "topic_write_interval": topic_write_eco2_interval,
            "topic_cmd_get": topic_cmd_get_eco2,
            "format": "%0.0f ppm"
        }
    }
    
    function_pressure = {
        "installation_id": installation_id,
        "type": 'pressure',
        "meta": {
            "device_id": str(device_id),
            "name": mac + " pressure",
            "topic_read": topic_read_pressure,
            "topic_read_interval": topic_read_pressure_interval,
            "topic_write_interval": topic_write_pressure_interval,
            "topic_cmd_get": topic_cmd_get_pressure,
            "format": "%0.2f hPa"
        }
    }

    function_status = {
        "installation_id": installation_id,
        "type": 'boolean_text',
        "meta": {
            "device_id": str(device_id),
            "name": mac + " status",
            "state_true": '1',
            "state_false": '0',
            "text_true": "Online",
            "text_false": "Offline",
            "topic_read": topic_status,
            "topic_cmd_ping": topic_cmd_ping,
            "topic_evt_pong": topic_evt_pong,
            "topic_uptime": topic_uptime
        }
    }

    lynx.create_function_if_needed(function_temperature)
    wdt.feed()
    lynx.create_function_if_needed(function_eco2)
    wdt.feed()
    lynx.create_function_if_needed(function_tvoc)
    wdt.feed()
    lynx.create_function_if_needed(function_pressure)
    wdt.feed()
    lynx.create_function_if_needed(function_status)
    wdt.feed()
    
wdt.feed()

create_lynx_objects()

wdt.feed()

last_temperature = 0
last_pressure = 0
last_eco2 = 0
last_tvoc = 0
last_ping = 0
last_uptime_report = 0

while True:
    try:
        client = mqtt_connect()
    except OSError as e:
        reconnect()
    
    load_intervals()
    # Let the world the settings we are using
    client.publish(client_id_prefix + topic_read_temperature_interval, '{ "value":' + str(temperature_interval) +  ', "timestamp": ' + str(time.time()) + ' }')
    client.publish(client_id_prefix + topic_read_pressure_interval, '{ "value":' + str(pressure_interval) +  ', "timestamp": ' + str(time.time()) + ' }')
    client.publish(client_id_prefix + topic_read_eco2_interval, '{ "value":' + str(eco2_interval) +  ', "timestamp": ' + str(time.time()) + ' }')
    client.publish(client_id_prefix + topic_read_tvoc_interval, '{ "value":' + str(tvoc_interval) +  ', "timestamp": ' + str(time.time()) + ' }')

    
    while True:
        ts = time.time()
        client.check_msg()

        wdt.feed()

        if ts - last_temperature > temperature_interval:
            temp = bmp.temperature
            client.publish(client_id_prefix + topic_read_temperature, '{ "value":' + str(temp) +  ', "timestamp": ' + str(time.time()) + ' }')
            last_temperature = time.time()
        if ts - last_pressure > pressure_interval:
            pressure = bmp.pressure
            client.publish(client_id_prefix + topic_read_pressure, '{ "value":' + str(pressure) +  ', "timestamp": ' + str(time.time()) + ' }')
            last_pressure = time.time()
        if ts - last_eco2 > eco2_interval:
            co2eq, tvoc = sgp.iaq_measure()
            client.publish(client_id_prefix + topic_read_eco2, '{ "value":' + str(co2eq) +  ', "timestamp": ' + str(time.time()) + ' }')
            last_eco2 = time.time()
        if ts - last_tvoc > tvoc_interval:
            co2eq, tvoc = sgp.iaq_measure()
            client.publish(client_id_prefix + topic_read_tvoc, '{ "value":' + str(tvoc) +  ', "timestamp": ' + str(time.time()) + ' }')
            last_tvoc = time.time()


        if ts - last_ping > 5:
            last_ping = ts
            led_flash(led)
            client.ping()

        if ts - last_uptime_report > 600:
            last_uptime_report = ts
            client.publish(client_id_prefix + topic_uptime, '{ "value":' + str(ts - boot_time) +  ', "timestamp": ' + str(time.time()) + ' }')
