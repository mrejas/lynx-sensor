# Network connection handler

import network
import ubinascii
import time

class Network:
    def __init__(self, config):
        self.ssid = config['ssid']
        self.password = config['password']
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.mac = ubinascii.hexlify(self.wlan.config('mac'),':').decode()

    def connect(self):
        self.wlan.connect(self.ssid, self.password)

        # Wait for connect or fail
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
                max_wait -= 1
                print('Waiting for connection...')
                time.sleep(1)

        # Handle connection error
        if self.wlan.status() != 3:
            print(self.wlan.status())
            raise RuntimeError('Network connection failed')
        else:
            print('Connected')

    def ifconfig(self):
        return(self.wlan.ifconfig())
