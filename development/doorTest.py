import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)  #Power
GPIO.setup(13, GPIO.OUT)  #Extend


try:
    while 1:
        GPIO.output(6,False)
        GPIO.output(13,True)

except KeyboardInterrupt:
    GPIO.cleanup()

finally:
    GPIO.cleanup()
