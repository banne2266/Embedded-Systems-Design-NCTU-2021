import RPi.GPIO as GPIO
import dht11
import time
import datetime

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

LED_PIN = 17
GPIO.setup(LED_PIN, GPIO.OUT)

# read data using pin 
instance = dht11.DHT11(pin=4)

try:
    while True:
        result = instance.read()
        if result.is_valid():
            print("Last valid input: " + str(datetime.datetime.now()))

            print("Temperature: %-3.1f C" % result.temperature)
            print("Humidity: %-3.1f %%" % result.humidity)
            
            if result.temperature >= 20:
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                GPIO.output(LED_PIN, GPIO.LOW)

        time.sleep(1)

except KeyboardInterrupt:
    print("Cleanup")

finally:
    GPIO.cleanup()