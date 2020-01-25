import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(5,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


## using wiring similar to https://www.build-electronic-circuits.com/ldr-circuit-diagram/



try:
    while 1:
        print(GPIO.input(5))
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
