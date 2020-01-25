import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)

try:
    pass
    while 1:
        GPIO.output(12,1)
        GPIO.output(16,0)
        time.sleep(2)
        GPIO.output(12,0)
        time.sleep(1)
        GPIO.output(12,0)
        GPIO.output(16,1)
        time.sleep(2)
        GPIO.output(12,0)
        break

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
