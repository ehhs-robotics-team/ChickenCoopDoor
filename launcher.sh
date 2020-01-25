#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script , then back home

# From tutorial at https://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/
# Or try commenting out one of the lines after running "sudo crontab -e"
#cd /
#cd /home/pi/Desktop/ChickenCoopDoor
/usr/bin/python3 /home/pi/Desktop/ChickenCoopDoor/simple_door3.py > error.log &
#cd /


