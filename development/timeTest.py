import datetime
from astral import Location
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
myHostname = "192.168.2.37"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40,GPIO.OUT)


# Get sunrise and sunset for Wardensville, WV
l = Location()
l.latitude = 39.084574
l.longitude = -78.592021
l.timezone = 'US/Eastern'

sunrise = l.sun()['dawn']
sunriseHour = sunrise.strftime('%H')

sunset = l.sun()['sunset']
sunsetHour = sunset.strftime('%H')


state = False
try:
    while 1:
        if (int(sunriseHour) < datetime.datetime.now().hour < int(sunsetHour)-2) != state:
            state = not state 
            GPIO.output(40,state)
            publish.single("ledStatus", int(state), hostname=myHostname)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
