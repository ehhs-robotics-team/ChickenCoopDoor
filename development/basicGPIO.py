import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32,GPIO.OUT)

try:
    while 1:
        GPIO.output(32,True)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
