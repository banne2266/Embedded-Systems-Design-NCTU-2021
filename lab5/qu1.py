import schedule
import time
import picamera
def job():
    print("I'm working...")
    with picamera.PiCamera() as camera:
        camera.start_preview()
        for i, filename in enumerate(camera.capture_continuous('image{counter:02d}.jpg')):
            print(filename)
            time.sleep(1)
            if i == 59:
                break
                
schedule.every(20).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
   

