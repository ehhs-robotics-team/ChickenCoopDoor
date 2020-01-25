import datetime
from astral import Location
import pytz
import time


# Get sunrise and sunset for Wardensville, WV
loc = Location()
loc.latitude = 39.084574
loc.longitude = -78.592021
loc.timezone = 'US/Eastern'

TIMEZONE = pytz.timezone('US/Eastern')

def openTime(date):   # Calculate the hour of sunrise for given date
    sunrise = loc.dawn(date = date)
    sunriseTime = sunrise.strftime("%x %X (%Z)")
    print(sunriseTime)
    return sunrise

def closeTime(date):  # Calculate the hour of sunset for the given date
    
    
    sunset = loc.dusk(date = date)
    sunsetTime = sunset.strftime("%x %X (%Z)")
    print(date.strftime("%x %X (%Z)"))
    print(sunsetTime)
    return sunset 


today = datetime.datetime.now(TIMEZONE)
tomorrow = today + datetime.timedelta(days=1)
while 1:
	today = datetime.datetime.now(TIMEZONE)
	closeTime()
	time.sleep(5)
#sunrise = loc.sun()['dawn']
#sunriseHour = sunrise.strftime('%H')
#sunriseMinute = sunrise.strftime('%M')
#print( 'sunrise hour='+str(sunriseHour))
#print( 'sunrise minute='+str(sunriseMinute))

#sunset = loc.sun()['sunset']
#sunsetHour = sunset.strftime('%H')
#sunsetMinute = sunset.strftime('%M')
#print( 'sunset hour='+str(sunsetHour))
#print( 'sunset minute='+str(sunsetMinute))

