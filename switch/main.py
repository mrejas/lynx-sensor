from wifi_network import Network
import time
from machine import Pin
import machine
from umqtt.robust import MQTTClient
import ubinascii
import json
import ntptime
import utime
from lynx import Lynx
from led_utils import *
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
mac = net.mac

wdt.feed()

ntptime.settime()

wdt.feed()

year, month, day, hour, mins, secs, weekday, yearday = time.localtime()   
print('Time set: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} UTC'.format(year, month, day, hour, mins, secs) )

led_blink(led, 3)
boot_time = time.time()


switch1_out = Pin(17, Pin.OUT)
switch1_in = Pin(16, Pin.IN, pull=Pin.PULL_DOWN)


client_id = ubinascii.hexlify(machine.unique_id())


topic_write = 'set/rejaswifi/' + mac + '/switch/'
topic_read = 'obj/rejaswifi/' + mac + '/switch/'
topic_status = 'obj/rejaswifi/' + mac + '/alive'

wdt.feed()

def control_out(switch, value):
    if switch == 1:
        _out = switch1_out
    else:
        return
        
    if value == 0:
        _out.off()
        client.publish(client_id_prefix + topic_read + str(switch), '{"value": 0, "timestamp": ' + str(time.time()) + ' }')
    else:
        _out.on()
        client.publish(client_id_prefix + topic_read + str(switch), '{ "value": 255, "timestamp": ' + str(time.time()) + ' }')
    

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    switch_id = topic.decode('utf-8').split('/')[5]
    data = json.loads(msg);
    if switch_id == '1':
        print('Setting 1')
        control_out(1, data['value'])


wdt.feed()

def mqtt_connect():
    print('Trying to connect MQTT')
    client = MQTTClient(client_id, mqtt_broker,
                        user=b'picosensor',
                        password=mqtt_password,
                        port=8883,
                        ssl=mqtt_ssl,
                        keepalive=30)
    client.set_callback(sub_cb)
    client.set_last_will(client_id_prefix + topic_status, '{"value": 0}')
    client.connect()
    client.subscribe(client_id_prefix + topic_write + '+')
    client.publish(client_id_prefix + topic_status, '{"value": 1}')
    print('Connected to %s MQTT Broker'%(mqtt_server))
    led_blink(led, 5)
    return client

wdt.feed()

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

wdt.feed()

def create_lynx_objects():
    lynx = Lynx(lynx_api, installation_id, lynx_api_key)
    
    device = {
        "installation_id": installation_id,
        "type": "rejaswifi",
        "meta": {
            "name": "WiFi SWITCH: " + mac,
            "mac": mac
        }
    }
    
    device_id = lynx.create_device_if_needed(device)
    
    
    function_switch = {
        "installation_id": installation_id,
        "type": 'switch',
        "meta": {
            "device_id": str(device_id),
            "name": mac + " switch",
            "state_on": '255',
            "state_off": '0',
            "topic_read": topic_read + '1',
            "topic_write": topic_write + '1'
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
            "topic_read": topic_status
        }
    }

    lynx.create_function_if_needed(function_switch)
    lynx.create_function_if_needed(function_status)
    

wdt.feed()

create_lynx_objects()

wdt.feed()

pressed = 0
last_ping = 0
last_uptime_report = 0

while True:
    try:
        client = mqtt_connect()
    except OSError as e:
        reconnect()
    
    while True:
        ts = time.time()
        client.check_msg()

        wdt.feed()

        if switch1_in.value() == 1:
            if pressed != 1:
                print('Publish ...')
                if switch1_out.value() == 1:
                    sub_cb(bytes(client_id_prefix + topic_write + '1', 'utf-8'), '{"value":0}')
                else:
                    sub_cb(bytes(client_id_prefix + topic_write + '1', 'utf-8'), '{"value":255}')
                pressed = 1
            #time.sleep(0.5) # Debounce
        else:
            pressed = 0
            
        if ts - last_ping > 5:
            last_ping = ts
            led_flash(led)
            client.ping()

        if ts - last_uptime_report > 600:
            last_uptime_report = ts
            client.publish(client_id_prefix + topic_uptime, '{ "value":' + str(ts - boot_time) +  ', "timestamp": ' + str(time.time()) + ' }')
