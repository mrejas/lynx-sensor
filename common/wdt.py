#
# This file is only used to disable the watchdog manually
#
import machine

# Disable wdt
machine.mem32[0x40058000] = machine.mem32[0x40058000] & ~(1<<30)