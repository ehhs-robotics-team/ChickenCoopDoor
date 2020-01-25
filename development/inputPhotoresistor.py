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
        if GPIO.input(36) == True:
            state = 1
            #print("Port 36, HIGH")
            #publish.single("ledStatus", 1, hostname=myHostname)
            #GPIO.output(40,1)
        else:
            state = 0
            #GPIO.output(40,0)
            #print("Port 36, LOW")
            #publish.single("ledStatus", 0, hostname=myHostname)
        #sleep(0.1)
        GPIO.output(40,state)
        publish.single("ledStatus", state, hostname=myHostname)
            

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
