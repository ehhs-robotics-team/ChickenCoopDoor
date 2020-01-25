#!/usr/bin/python3

import time
from time import sleep
import RPi.GPIO as GPIO
import datetime
from astral import Location
import pytz
import settings

import smtplib


ID = "#1"
TIMEZONE = pytz.timezone('US/Eastern')


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


DOOR_TIMEOUT = 120 ## Constant for the maximum length of time the door should take to close.
LIGHT_DELAY = 600 # Ten minutes

## List of Email adresses to send error emails and updates to:
#EMAIL_TO = []
#EMAIL_TO = ['josh@wardensvillegardenmarket.org']
EMAIL_TO = ['ehhsnerdz@gmail.com']
#EMAIL_TO = ["darzgood@gmail.com"]

def setLocal():
    # Set timezone and location for Wardensville, WV
    logOutput("Setting up the timezone and location for Wardensville, WV...")
    
    global loc
    loc = Location()
    loc.latitude = 39.084574
    loc.longitude = -78.592021
    loc.timezone = 'US/Eastern'
    
def logData(data):
    '''Log time data
    Used only for recording open and close times.'''
    with open("/home/pi/Desktop/ChickenCoopDoor/data.log", "a") as datalog:
        datalog.write(data +"\n")

def logOutput(data):
    '''Log all other info about program status, errors, emails, etc'''
    now = datetime.datetime.now(TIMEZONE).strftime("%x %X (%Z)")
    with open("/home/pi/Desktop/ChickenCoopDoor/update.log", "a") as datalog:
        datalog.write("{0}:\t{1}\n".format(now,data))
        
        
def sendEmail(message):
    gmail_user = settings.gmail_user  
    gmail_password = settings.gmail_password

    sent_from = gmail_user  
    to = EMAIL_TO 
    subject = 'Chicken Coop Door Update'  
    body = message + "\nMessage Sent: " + datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%x %X (%Z)")

    email_text = '''From: {0}\nTo: {1}\nSubject: {2}\n\n{3}\n\n'''.format(sent_from, ", ".join(to), subject, body)

    try:  
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        logOutput("Email sent: '{0}'".format(message))
    except:  
        logOutput("Something went wrong with sending this email: '{0}'".format(message))

        
def openDoor():   # Raise the door by powering AIN1 and grounding AIN2
    logOutput("Door opening...")
    
    GPIO.output(MOTOR_POSITIVE,False)
    GPIO.output(MOTOR_NEGATIVE,True)
    sleep(DOOR_TIMEOUT)
    deactivateDoor()
    
    
    now = datetime.datetime.now(TIMEZONE).strftime("%x %X (%Z)")
    #Make the output human friendly
    if (getDoorPosition() == 1): #It opened correctly
        logOutput("Door opened at: {0}".format(now))
        logData("Opened: {0}".format(now))
        sendEmail("Chicken coop door {1} opened: {0}".format(now, ID))
    else:
        logOutput("Door Failed to open at: {0}".format(now))
        logData("Failed open: {0}".format(now))
        sendEmail("Alert: Chicken coop door {0} didn't open correctly. Please check it.".format(ID))
        
def closeDoor():   # Lower the door by powering AIN1 and grounding AIN2
    logOutput("Door Closing...")
    
    GPIO.output(MOTOR_POSITIVE,True)
    GPIO.output(MOTOR_NEGATIVE,False)
    sleep(DOOR_TIMEOUT)    
    deactivateDoor()

    now = datetime.datetime.now(TIMEZONE).strftime("%x %X (%Z)")
    
    if (getDoorPosition() == -1): #It closed correctly
        logOutput("Door closed at: {0}".format(now))
        logData("Closed: {0}".format(now))
        sendEmail("Chicken coop door {1} closed: {0}".format(now, ID))
    else:
        logOutput("Door failed to close at: {0}".format(now))
        logData("Failed close: {0}".format(now))
        sendEmail("Alert: Chicken coop door {0} didn't close correctly. Please check it.".format(ID)) 
    
def deactivateDoor():
    GPIO.output(MOTOR_POSITIVE, False)
    GPIO.output(MOTOR_NEGATIVE, False)

def getDoorPosition():
    """Read sensors to determine whether the coop door is up or down.
    -1=Down, 1=Up, 0=Unknown """
    logOutput("Determining door position...")
    doorPosition = 0  # Assume the door should be closed
    if GPIO.input(SWITCH_TOP):
        logOutput("Door found to be open")
        doorPosition = 1
    elif GPIO.input(SWITCH_BOTTOM):
        logOutput("Door found to be closed")
        doorPosition = -1
    else:
        logOutput("Failed to determine door position...")
        doorPosition = 0
        
    return doorPosition

# Timing methods
    
def openTime(date):   # Calculate the hour of sunrise
    sunrise = loc.dawn(date = date)
    sunriseTime = sunrise.strftime("%x %X (%Z)")
    return sunrise

def closeTime(date):  # Calculate the hour of sunset
    sunset = loc.dusk(date = date)
    sunsetTime = sunset.strftime("%x %X (%Z)")
    return sunset       
    
def getNextMoveTime(doorPosition):
    '''
    returns the time for the next action for the door, 
    checking to make sure it is the next time and not the previous:
    '''
    
    today = datetime.datetime.now(TIMEZONE)
    tomorrow = today + datetime.timedelta(days=1)
    if (doorPosition == -1): #Door is closed
        oTime = openTime(date=today)
        
        logOutput("Tentative open time: "+oTime.strftime("%x %X (%Z)"))
        if today >= oTime:
            logOutput("Oops, that was yesterday's opening time")
            oTime = openTime(date = tomorrow)
        logOutput("Next open time: " + oTime.strftime("%x %X (%Z)"))
        return oTime
    elif (doorPosition == 1): #Door is open
    
        cTime = closeTime(date = today)
        logOutput("Tentative close time: "+cTime.strftime("%x %X (%Z)"))
        if today >= cTime:
            logOutput("Oops, that was yesterday's closing time")
            cTime = closeTime(date = tomorrow)
        logOutput("Next close time: " + cTime.strftime("%x %X (%Z)"))
        return cTime
    else:   
        logOutput("Error: getNextMoveTime called without a valid door position")
        return tomorrow
         
def initializeDoorByTime(doorPosition=0):
    """
    Set the door to the correct position for the calculated time.
    Run once at boot.
    """
    
    now = datetime.datetime.now(TIMEZONE)
    
    oTime = openTime(date=now)
    cTime = closeTime(date=now)
    
    if (now < oTime) or (now > cTime): #Before dawn, after dusk
        if (doorPosition == -1): #Door is already closed
            pass
        else:
            closeDoor()
            doorPosition = -1
    else: # oTime <= now <= cTime:  # During daytime
        if (doorPosition == 1): #Door is already open
            pass
        else:
            openDoor()
            doorPosition = 1
            
    return doorPosition
    
        
def runByTime(doorPosition):
    '''Activates the chicken coop door based on dawn and dusk calculations 
    from on astral.'''
    
    doorPosition = initializeDoorByTime(doorPosition)
    
    if getDoorPosition() == 0: #The door is not recognized at either the up or down positions
        sendEmail("Critical Alert: Chicken coop door {0} could not be initialized. \
Please make sure that both the door and the sensors are working correctly. \
Continuing with runtime procedure.".format(ID))
        
    
    while (1):
        now = datetime.datetime.now(TIMEZONE)
        nextMoveTime = getNextMoveTime(doorPosition)
        waitTime = (nextMoveTime-now).total_seconds()
        
        sleep(waitTime)
        
        if doorPosition == 1:
            closeDoor()
            doorPosition = -1
        else:
            openDoor()
            doorPosition = 1
            
# Light methods
def checkAmbientLight():
    return GPIO.input(PHOTORESISTOR)
  
def runByLight(doorPosition):
    '''Activates the chicken coop door based on light levels detected.'''
    
    delay = LIGHT_DELAY
    #delay = 60  # Testing purposes: 1 minute
    
    if doorPosition == 0: # Check for an undefined door position
        openDoor()
        doorPosition = 1
     
    while(1):
        lightLevel = checkAmbientLight()
        
        if doorPosition == 1 and checkAmbientLight() == 1: #Door is up and it's light
            pass
        elif doorPosition == -1 and checkAmbientLight() == 0: #Door is down and it's dark
            pass
        
        elif doorPosition == 1 and checkAmbientLight() == 0: #Door is up but it's dark
            logOutput(datetime.datetime.now(TIMEZONE).strftime("%x %X (%Z)")+" -- It's dark out there")
            closeDoor()
            doorPosition = -1
            
        elif doorPosition == -1 and checkAmbientLight() == 1: #Door is down but it's light
            logOutput(datetime.datetime.now(TIMEZONE).strftime("%x %X (%Z)")+" -- It's light out there")
            openDoor()
            doorPosition = 1
        
        sleep(delay);
        
    
def main():
    sendEmail("The program for chicken coop door {0} has started! \
If you did not restart it, please check that it is still working correctly. \
The system could be having power issues.".format(ID))
    setLocal()
    
    doorPosition = getDoorPosition()
    if (doorPosition == 0): #The door is neither up nor down
        sendEmail("Alert: The position of chicken coop door {0} could not be determined. Attempting to auto initialize.".format(ID))
    
    runByTime(doorPosition)
    ## Or...
    #runByLight(doorPosition) 

try:
    main()

except (KeyboardInterrupt):
    pass

finally:
    sendEmail("Critical Alert: The program for chicken door {0} has died. Please restart it.".format(ID))
    GPIO.cleanup()
