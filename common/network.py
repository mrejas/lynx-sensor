# Network connection handler

import network

class Network:
    def __init__(self, config):
        self.ssid = config['ssid']
        self.password = config['password']
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self):
        self.wlan.connect(ssid, password)

        # Wait for connect or fail
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)

            # Handle connection error
            if wlan.status() != 3:
                 raise RuntimeError('Network connection failed')
            else:
                print('Connected')

    def ifconfig(self):
        return(self.wlan.ifconfig())
