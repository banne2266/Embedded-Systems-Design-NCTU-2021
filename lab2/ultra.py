import RPi.GPIO as GPIO
import time

v = 343
TRIGGER_PIN = 37
ECHO_PIN = 18
LED_PIN = 11

#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure():
    GPIO.output(TRIGGER_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, GPIO.LOW)
    pulse_start = time.time()
    print("measure start")
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        pulse_end = time.time()
    t = pulse_end - pulse_start
    d = t * v
    d /= 2
    return d * 100


try:
    while True:
        dis = measure()
        print("The distance is:" + str(dis))
        if dis < 30:
            for i in range(5):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.1)
        elif dis < 100:
            for i in range(2):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.4)
        else:
            time.sleep(1)

except KeyboardInterrupt:
    print("Cleanup")

finally:
    GPIO.cleanup()


