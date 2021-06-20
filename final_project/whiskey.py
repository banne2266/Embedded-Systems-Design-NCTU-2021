import RPi.GPIO as GPIO

class whiskey:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
        GPIO.output(self.pin, GPIO.LOW)
        
    def start(self):
        GPIO.output(self.pin, GPIO.HIGH)
    
    def stop(self):
        GPIO.output(self.pin, GPIO.LOW)
    