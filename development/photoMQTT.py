import time
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.publish as publish
myHostname = "192.168.2.37"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40,GPIO.OUT)
GPIO.setup(36,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


state = 0
try:
    while 1:
        if GPIO.input(36) != state:
            state = GPIO.input(36)
            GPIO.output(40,state)
            publish.single("ledStatus", state, hostname=myHostname)
            
            

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
