import paho.mqtt.publish as publish
import time
myHostname = "192.168.2.37"

print("Sending 0...")
publish.single("ledStatus", 0, hostname=myHostname)
time.sleep(1)
print("Sending 1...")
publish.single("ledStatus", 1, hostname=myHostname)


