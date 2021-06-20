import RPi.GPIO as GPIO

class sg90:
    def __init__(self, pwm_pin, GPIO_mode = GPIO.BCM, cycle = 2):
        GPIO.setmode(GPIO_mode)
        GPIO.setup(pwm_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pwm_pin, 50)
        self.cycle = cycle
        self.pwm.ChangeDutyCycle(cycle)#2~12
        self.pwm.start(cycle)
    
    def get_cycle(self):
        return self.cycle
        
    def change_dutycycle(self, cycle):
        if cycle > 12 or cycle < 2:
            raise ValueError("cycle shoud be between 2 to 12.")
        self.pwm.ChangeDutyCycle(cycle)#2~12
        self.cycle = cycle
    
    
        
    def change_angle(self, degree):
        cycle = degree / 18 + 2
        self.change_dutycycle(cycle)
        self.cycle = cycle
        
            