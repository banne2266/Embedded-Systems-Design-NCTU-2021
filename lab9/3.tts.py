from gtts import gTTS
import os

import RPi.GPIO as GPIO
import dht11
import time
import datetime
import speech_recognition as sr



# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

LED_PIN = 17
GPIO.setup(LED_PIN, GPIO.OUT)

# read data using pin 
instance = dht11.DHT11(pin=4)



#obtain audio from the microphone
r=sr.Recognizer() 

with sr.Microphone() as source:
    print("Please wait. Calibrating microphone...") 
    #listen for 1 seconds and create the ambient noise energy level 
    r.adjust_for_ambient_noise(source, duration=1) 
    print("Say something!")
    audio=r.listen(source)

# recognize speech using Google Speech Recognition 
try:
    print("Google Speech Recognition thinks you said:")
    t = r.recognize_google(audio).lower()
    print(t)
    if t == "let's go":
        while True:
            result = instance.read()
            if result.is_valid():
                print("Last valid input: " + str(datetime.datetime.now()))
                

                print("Temperature: %-3.1f C" % result.temperature)
                print("Humidity: %-3.1f %%" % result.humidity)
                
                
                text = "現在溫度是 %-3.1f 度" % result.temperature
                
                tts = gTTS(text=text, lang='zh')
                tts.save('hello.mp3')
                
                os.system('omxplayer -o local -p hello.mp3 > /dev/null 2>&1')
                
                time.sleep(2)
                
                break


            time.sleep(1)
    
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("No response from Google Speech Recognition service: {0}".format(e))
except KeyboardInterrupt:
    print("Cleanup")

finally:
    GPIO.cleanup()




