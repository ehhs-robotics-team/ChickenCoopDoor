import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

SWITCH_TOP    = 6
SWITCH_BOTTOM = 13

GPIO.setup(SWITCH_BOTTOM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Bottom switch
GPIO.setup(SWITCH_TOP,    GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Top switch

## using wiring similar to https://www.build-electronic-circuits.com/ldr-circuit-diagram/



try:
    while 1:
        print(GPIO.input(SWITCH_BOTTOM),GPIO.input(SWITCH_TOP))
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
