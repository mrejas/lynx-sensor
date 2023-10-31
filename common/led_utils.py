#
# Some utils for led output
#
import time

def led_blink(gpio, count):
    while count > 0:
        gpio.on()
        time.sleep(0.2)
        gpio.off()
        time.sleep(0.2)        
        count = count - 1

def led_flash(gpio):
        gpio.on()
        time.sleep(0.02)
        gpio.off()
        time.sleep(0.02)

