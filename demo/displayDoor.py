#!/usr/bin/python3

import time
from time import sleep
import RPi.GPIO as GPIO
import datetime
from astral import Location
import pytz
import timeout_decorator
import smtplib
import logging
import tkinter as tk
from context import settings


ID = "#1"


## Even GPIO pins are outputs, odd pins are sensors.
MOTOR_POSITIVE= 12  # Connected to AIN1 on the TB6612 motor driver
MOTOR_NEGATIVE= 16  # Connected to AIN2 on the TB6612 motor driver
SWITCH_TOP    = 6
SWITCH_BOTTOM = 13
PHOTORESISTOR = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_POSITIVE,GPIO.OUT) # Power
GPIO.setup(MOTOR_NEGATIVE,GPIO.OUT) # Control
GPIO.setup(SWITCH_BOTTOM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Bottom switch
GPIO.setup(SWITCH_TOP,    GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Top switch
GPIO.setup(PHOTORESISTOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Photoresistor

## Constant for the maximum length of time the door should take to close.
DOOR_TIMEOUT = 75    # In seconds
LIGHT_TIMEOUT = 3600 # One hour

## List of Email adresses to send error emails and updates to:
#EMAIL_TO = []

#EMAIL_TO = ['josh@wardensvillegardenmarket.org']
EMAIL_TO = ['ehhsnerdz@gmail.com']
EMAIL_TO = ["darzgood@gmail.com"]


#from imp import reload
#reload(logging)
#logging.basicConfig(filename='start@_{0}.log'.format(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d_%H:%M:%S")), format='%(asctime)s %(message)s', level=logging.DEBUG, filemode='a')
logging.basicConfig(filename='demo.log', format='%(asctime)s %(message)s', level=logging.DEBUG, filemode='a')


def setLocal():
    # Set timezone and location for Wardensville, WV
    logging.info("Setting up the timezone and location for Wardensville, WV...")
    
    global loc
    loc = Location()
    loc.latitude = 39.084574
    loc.longitude = -78.592021
    loc.timezone = 'EST'
    
    
    

class DoorTimeoutError(Exception):
    pass
    
    
class LightTimeoutError(Exception):
    pass

    
def useDoor(direction):
    '''direction: True = Open, False = Close'''
    now = datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
    nowEST = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S") #Make the output human friendly
    if direction:
        try:
            logging.debug("Door Opening...")
            doorOpen()
            logging.debug("Door Opened at: {0}".format(now))
            writeToFile("Opened: {0} (EST)".format(nowEST))
            sendEmail("Chicken coop door {0} opened correctly.".format(ID))
                
        except DoorTimeoutError:
            doorDeactivate()
            logging.error("Door Failed to Open at: {0}".format(now))
            writeToFile("Failed Open: {0} (EST)".format(nowEST))
            sendEmail("Chicken coop door {0} didn't open correctly. If you did not leave it on Manual, please check it.".format(ID))

    else:
        try:
            logging.debug("Door Closing...")
            doorClose()
            logging.debug("Door Closed at: {0}".format(now))
            writeToFile("Closed: {0} (EST)".format(nowEST))
            sendEmail("Chicken coop door {0} closed correctly.".format(ID))
        except DoorTimeoutError:
            doorDeactivate()
            logging.error("Door failed to Close at: {0}".format(now))
            writeToFile("Failed Close: {0} (EST)".format(nowEST))
            sendEmail("Chicken coop door {0} didn't close correctly. If you did not leave it on Manual, please check it.".format(ID))

# Time out after 5 seconds and throw an exception to tell if the door didn't
# close correctly.
@timeout_decorator.timeout(DOOR_TIMEOUT, timeout_exception = DoorTimeoutError)        
def doorClose():   # Lower the door by powering AIN1 and grounding AIN2
    while not GPIO.input(SWITCH_BOTTOM):
        GPIO.output(MOTOR_POSITIVE,True)
        GPIO.output(MOTOR_NEGATIVE,False)
        #print(GPIO.input(SWITCH_BOTTOM))
        sleep(0.05)
    doorDeactivate()

# Time out after 5 seconds and throw an exception to tell if the door didn't
# open correctly.
@timeout_decorator.timeout(DOOR_TIMEOUT, timeout_exception = DoorTimeoutError)
def doorOpen():   # Raise the door by powering AIN1 and grounding AIN2
    while not GPIO.input(SWITCH_TOP):
        GPIO.output(MOTOR_POSITIVE,False)
        GPIO.output(MOTOR_NEGATIVE,True)
        #print(GPIO.input(SWITCH_TOP))
        sleep(0.05)
    doorDeactivate()
    
def doorDeactivate():
    GPIO.output(MOTOR_POSITIVE, False)
    GPIO.output(MOTOR_NEGATIVE, False)
    
        
def writeToFile(data):
    with open("/home/pi/Desktop/ChickenCoopDoor/demo.log", "a") as datalog:
        datalog.write(data +"\n")


def sendEmail(message):
    gmail_user = settings.gmail_user  
    gmail_password = settings.gmail_password

    sent_from = gmail_user  
    to = EMAIL_TO 
    subject = 'Chicken Coop Door Update'  
    body = message + "\n Sent at: {}".format(datetime.datetime.now())

    email_text = '''From: {0}\nTo: {1}\nSubject: {2}\n\n{3}\n\n'''.format(sent_from, ", ".join(to), subject, body)

    try:  
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        logging.debug("Email sent: '{0}'".format(message))
    except:  
        logging.error("Something went wrong with sending this email: '{0}'".format(message))
    

def openTime(date = datetime.datetime.now(tz=pytz.UTC)):   # Calculate the hour of sunrise
    sunrise = loc.dawn(local=False, date = date)
    sunriseTime = sunrise.strftime('%H:%M:%S')
    return sunrise

def closeTime(date = datetime.datetime.now(tz=pytz.UTC)):  # Calculate the hour of sunset
    sunset = loc.dusk(local=False, date = date)
    sunsetTime = sunset.strftime('%H:%M:%S')
    return sunset

def getDoorState():
    """Read sensors to determine whether the coop door is up or down.
    If neither, the door is automatically closed.
    False = Down, True = Up"""
    logging.debug("Determining door position...")
    doorState = False  # Assume the door should be closed
    if GPIO.input(SWITCH_TOP):
        logging.info("Door found to be Open")
        doorState = True
    elif GPIO.input(SWITCH_BOTTOM):
        logging.info("Door found to be Closed")
        doorState = False
    else:
        logging.warning("Failed to determine door position...")
        useDoor(False)
        doorState = False
        
    return doorState
    
def doorStart():
    '''Open or close the door the first time based on astral.'''

    doorState = getDoorState()
    now = datetime.datetime.now(tz=pytz.UTC) # UTC current time
    oTime = openTime()   # UTC dawn according to astral
    cTime = closeTime()  # UTC dusk according to astral
    if (oTime < now < cTime) != doorState:
        doorState = not doorState
        logging.info("Starting door {0} based on astral".format("open" if doorState else "closed"))
        useDoor(doorState)
    else:
        pass
    return doorState, now
    

def doorIdleUntil(nextMoveTime):
    '''Sleep in five minute increments until nextMovetime:
    '''
    doNothing = True
    while doNothing:
        now = datetime.datetime.now(tz=pytz.UTC) # UTC current time
        if now > nextMoveTime:
            logging.debug("The waiting is over. The time is now. (The door has stopped idling)")
            doNothing = False
        else:
            sleep(300)
            
def getNextMoveTime(doorState, lastMoveTime):
    '''
    returns the time for the next action for the door, 
    checking to make sure it is the next time and not the previous:
    '''
    
    today = datetime.datetime.now(tz=pytz.UTC)
    tomorrow = today + datetime.timedelta(days=1)
    if not doorState:
        oTime = openTime()
        
        logging.info("New open time: "+oTime.strftime('%m-%d-%Y %H:%M:%S'), "last move time: "+lastMoveTime.strftime('%m-%d-%Y %H:%M:%S'))
        if lastMoveTime >= oTime:
            logging.debug("Oops, that was yesterday's opening time")
            oTime = openTime(date = tomorrow)
        logging.info("next open time is: " + oTime.strftime('%m-%d-%Y %H:%M:%S'))
        return oTime
    else:
        cTime = closeTime()
        if lastMoveTime >= cTime:
            logging.debug("Oops, that was yesterday's closing time")
            cTime = closeTime(date = tomorrow)
        logging.info("next close time is: " + cTime.strftime('%m-%d-%Y %H:%M:%S'))
        return cTime

    
        
        
def checkAmbientLight():
    return GPIO.input(PHOTORESISTOR)

@timeout_decorator.timeout(LIGHT_TIMEOUT, timeout_exception = LightTimeoutError) #It should have moved after an hour...
def waitForLightChange(doorState):
    while True:
        sleep(1)
        if doorState == True and checkAmbientLight() == 1:
            pass
        elif doorState == False and checkAmbientLight() == 0:
            pass
        
        elif doorState == True and checkAmbientLight() == 0:
            logging.debug("It's dark out there")
            useDoor(False)
            break
        elif doorState == False and checkAmbientLight() == 1:
            logging.debug("It's light out there")
            useDoor(True)
            break
    return not doorState
    
def moveAtLightChange(doorState):
    '''
    Tries to wait for the light to change to move the door, but,
    after an hour, defaults to moving the door.
    '''
    try:
        doorState = waitForLightChange(doorState)
        logging.info("Door {1} within the time limit: {0} seconds.".format(LIGHT_TIMEOUT, "opened" if doorState else "closed"))
    except LightTimeoutError:
        doorState = not doorState
        useDoor(doorState)
        sendEmail("""There's a problem with the light sensor on 
chicken door {0}. The door was {1}, but later than it should
have been. Please make sure the light sensor is connected correctly.
        """.format(ID, "opened" if doorState else "closed"))
    
    return doorState
        
    
def setGui():
    root = tk.Tk()
    frame = tk.Frame(root, w=50%)
    frame.pack()
    UPbutton = tk.Button(frame, text="Raise", fg="green", command = doorOpen)
    DOWNbutton = tk.Button(frame, text="Lower", fg = "green", command = doorClose)
    STOPbutton = tk.Button(frame, text="Stop", fg = "red", command= doorDeactivate)
    
    UPbutton.pack()
    DOWNbutton.pack()
    STOPbutton.pack()
    
    root.mainloop()
    
    
def main():
    sendEmail("The program for chicken coop door {0} has started! \
If you did not restart it, please check that it is still working correctly. \
The sytem could be having power issues.".format(ID))
    setLocal()
    doorState, lastMoveTime = doorStart()
    setGui()
    while 1:
        pass
        #nextMoveTime = getNextMoveTime(doorState, lastMoveTime)
        #doorIdleUntil(nextMoveTime)
        #lastMoveTime = nextMoveTime
        #doorState = moveAtLightChange(doorState)


try:
    main()

except (KeyboardInterrupt):
    pass

finally:
    sendEmail("The chicken door program has died. Please restart it.")
    logging.shutdown()
    GPIO.cleanup()
