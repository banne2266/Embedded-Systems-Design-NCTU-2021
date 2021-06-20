import RPi.GPIO as GPIO
import time

STOP = 0
UP = 1
BACK = 2
RIGHT = 1
LEFT = 2

class Car:
    def __init__(self, left1, left2, right1, right2, left_pwm = None, right_pwm = None):
        self.left1 = left1
        self.left2 = left2
        self.right1 = right1
        self.right2 = right2
        self.state = STOP
        self.lr_state = STOP
        
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.left1, GPIO.OUT)
        GPIO.setup(self.left2, GPIO.OUT)
        GPIO.setup(self.right1, GPIO.OUT)
        GPIO.setup(self.right2, GPIO.OUT)
        
        if left_pwm is not None and right_pwm is not None :
            GPIO.setup(left_pwm, GPIO.OUT)
            GPIO.setup(right_pwm, GPIO.OUT)

            self.l_pwm = GPIO.PWM(left_pwm, 333)
            self.r_pwm = GPIO.PWM(right_pwm, 333)

            self.l_pwm.ChangeDutyCycle(75)
            self.r_pwm.ChangeDutyCycle(75)

    def set_left_direction(self, direction):
        if direction > 0: #forward
            GPIO.output(self.left1, GPIO.HIGH)
            GPIO.output(self.left2, GPIO.LOW)
        elif direction == 0:
            GPIO.output(self.left1, GPIO.LOW)
            GPIO.output(self.left2, GPIO.LOW)
        else:
            GPIO.output(self.left1, GPIO.LOW)
            GPIO.output(self.left2, GPIO.HIGH)
    
    def set_right_direction(self, direction):
        if direction > 0: #forward
            GPIO.output(self.right1, GPIO.HIGH)
            GPIO.output(self.right2, GPIO.LOW)
        elif direction == 0:
            GPIO.output(self.right1, GPIO.LOW)
            GPIO.output(self.right2, GPIO.LOW)
        else:
            GPIO.output(self.right1, GPIO.LOW)
            GPIO.output(self.right2, GPIO.HIGH)
    
    def stop(self):
        self.set_left_direction(0)
        self.set_right_direction(0)
        self.state = STOP
        self.lr_state = STOP

    def forward(self):
        self.set_left_direction(1)
        self.set_right_direction(1)
        self.state = UP
        self.lr_state = STOP

    def backward(self):
        self.set_left_direction(-1)
        self.set_right_direction(-1)
        self.state = BACK
        self.lr_state = STOP

    def right(self):
        self.set_left_direction(1)
        self.set_right_direction(-1)
        self.state = STOP
        self.lr_state = RIGHT
    
    def left(self):
        self.set_left_direction(-1)
        self.set_right_direction(1)
        self.state = STOP
        self.lr_state = LEFT
        

    def set_speed(self, speed):
        '''
            speed: 0 ~ 75
        '''
        if speed < 0 or speed > 75:
            raise ValueError("Speed shoud be between 0 to 75.")
        self.l_pwm.ChangeDutyCycle(speed)
        self.r_pwm.ChangeDutyCycle(speed)
    
    def control(self, key):
        print("Key:", key)
        if key == ord('w'):
            if self.state == STOP:
                self.forward()
            elif self.state == BACK:
                self.stop()
        elif key == ord('s'):
            if self.state == STOP:
                self.backward()
            elif self.state == UP:
                self.stop()
            
        elif key == ord('a'):
            if self.lr_state == STOP:
                self.left()
            elif self.lr_state == RIGHT:
                self.stop()
        elif key == ord('d'):
            if self.lr_state == STOP:
                self.right()
            elif self.lr_state == LEFT:
                self.stop()
        elif key == ord('z'):
            self.dance()
            
        elif key == ord('q'):
            self.stop()
        
    def dance(self):
        for i in range(3):
            self.left()
            time.sleep(0.4)
            self.right()
            time.sleep(0.4)
            self.forward()
            time.sleep(0.4)
            self.backward()
            time.sleep(0.4)
        
        self.stop()
    

        