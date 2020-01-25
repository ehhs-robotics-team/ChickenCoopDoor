import time
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.publish as publish
import paho.mqtt.client as mqttClient
myHostname = "192.168.2.37"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40,GPIO.OUT)
GPIO.setup(36,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)




 
def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
 
        print("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
 
        print("Connection failed")
 
def on_message(client, userdata, message):
    print("Message received: "  + str(message.payload))
    try:
        GPIO.output(40, int(message.payload))
    except ValueError:
        print("Message payload '{0}' not applicable.".format(message.payload))
 
Connected = False   #global variable for the state of the connectionstate = 0


client = mqttClient.Client("Python")               #create new instance
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback
 
client.connect(myHostname)          #connect to broker
 
client.loop_start()        #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)
 
client.subscribe("ledStatus")
try:
    while 1:
        sleep(1)
            
            

except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()

finally:
    GPIO.cleanup()
