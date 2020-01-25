import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32,GPIO.OUT)  #Power
GPIO.setup(36,GPIO.OUT)  #Extend

try:
    while 1:
        GPIO.output(32,True)
        GPIO.output(36,True)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
