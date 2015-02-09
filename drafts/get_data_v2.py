import io
import time
import picamera
import get_weight
import requests
import RPi.GPIO as GPIO
# import StringIO
# from PIL import Image
# import time

GPIO.setmode(GPIO.BCM)

enable_pin = 23
coil_A_1_pin = 4
coil_A_2_pin = 17
coil_B_1_pin = 27
coil_B_2_pin = 22

GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

GPIO.output(enable_pin, 1)

def forward(delay, steps):  
    delay = int(delay)/1000.0
    steps = int(steps)
    for i in range(0, steps):
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)

def backwards(delay, steps):
    delay = int(delay)/1000.0
    steps = int(steps)
    for i in range(0, steps):
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(1, 0, 1, 0)
        time.sleep(delay)

def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)


def outputs(samples, steps, weight, item_class):
    global start
    url_item = 'http://128.122.72.105:8000/ecan/upload/'
    url_bg = 'http://128.122.72.105:8000/ecan/upload-back_ground/'
    cont = 'n'
    print 'Prepare for back_ground capture'
    while cont != 'y':
        cont = raw_input("ready? [y] ")
        if cont != 'y':
            cont = 'n'
    stream = io.BytesIO()
    for i in range(samples +4):
        yield stream
        stream.seek(0)
        if i ==0:
            my_file_bg = stream
            data_bg = {'ecan':'1'}
            files_bg = {'im': my_file_bg}
            r = requests.post(url_bg, data = data_bg, files=files_bg)
            if r.json()['result'] == 'valid': bg_pk =r.json()['id']; print r.json()['result'], 'back_ground id: ', r.json()['id']
            else: print 'Operation not completed';
            print 'Place item'
            cont = 'n'
            while cont != 'y':
                cont = raw_input("ready? [y] ")
                if cont != 'y':
                    cont = 'n'
            start = time.time()
        elif i>3: 
            my_file = stream
            data_item = {'ecan':'1','bg': bg_pk, 'weight':weight, 'item_class':item_class}
            files_item = {'im': my_file}
            r = requests.post(
                              url_item, data=data_item, files=files_item)
            print r.text
            forward(5, steps)
        stream.truncate(0)
        stream.seek(0)


def get_data(samples, item_class):
    with picamera.PiCamera() as camera:
        camera.led = False
        global start
        start = 0
        camera.resolution = (1024, 768)
        camera.iso = 200
        camera.framerate = 10
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        weight = get_weight.get()
        steps = int(512 / samples)
        camera.capture_sequence(
                                outputs(samples, steps, weight, item_class),
                                'jpeg', use_video_port=True)
        finish = time.time()
        print'Captured %s' % samples + ' images in %.2fs' % (finish - start)
    return 'done'

def get_preview():
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.iso = 200
        camera.framerate = 10
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        camera.capture('sample.jpg')
        data = {'ecan':'1'}
        files = {'im': open('sample.jpg', 'rb')}
        url = 'http://128.122.72.105:8000/ecan/upload-sample/'
        r = requests.post(url, data = data, files=files)
        print r
    return 'done'


cont = 'y'
while cont == 'y':
    preview = raw_input("Preview? [y/n]")
    if preview == 'y':
        while preview == 'y':
            take= raw_input("Take? [y/n]")
            if take == 'y': get_preview()
            preview = raw_input("Keep doing this? [y/n]")
    samples = raw_input("Number of samples?")
    item_class = raw_input("What class? ")
    result = get_data(int(samples), item_class)
    print result
    cont = raw_input("Continue? [y/n] ")
    if cont != 'y' and cont != 'n':
        cont = 'n'
GPIO.cleanup()


### Code Recycling
## Imports

# import cv2
# import pygame.camera
# import pygame.image

# if upload_type == 'bg':
#   data = {'ecan':'1'}
#   files = {'back_ground': my_file}
#   url = 'http://128.122.72.105:8000/ecan/upload-back_ground/'
#   r = requests.post(url, data = data, files=files)
#   if r.json()['result'] == 'valid':
#       bg_pk =r.json()['id']
#       return bg_pk
#       print r.json()['result'], 'Back ground id: ', r.json()['id']
#   else: return 'Operation not completed'
# if upload_type == 'item':

# if samples <= 40: camera.capture_sequence(outputs(samples, steps, weight), 'jpeg', use_video_port=True)
# else: 
#   ints = int(samples/40)
#   new_samples = [40 for i in range(ints)]
#   if samples % 40 > 0: new_samples.append(samples % 40)
#   for e in new_samples:
#       camera.capture_sequence(outputs(e, steps, weight), 'jpeg', use_video_port=True)

# correct, img = cam.read()
# cam = cv2.VideoCapture(0) 
# if correct: cv2.imwrite('usb_cam/usb_cam.jpg',img) #save image