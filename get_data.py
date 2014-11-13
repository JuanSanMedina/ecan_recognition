import time
import picamera
import pygame.camera
import pygame.image
import get_weight
import requests
import RPi.GPIO as GPIO
import time
from cv2 import cv2

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

def take_picamera():
	with picamera.PiCamera() as camera:
		camera.led = False
		camera.capture('ir.jpg')

def take_usb():
	pygame.camera.init()
	cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
	cam.start()
	img = cam.get_image()
	pygame.image.save(img, "color.jpg")
	pygame.camera.quit()

take_picamera()
take_usb()

def get_data(samples, type):
	cam = cv2.VideoCapture(0)
	with picamera.PiCamera() as camera:
		
		camera.resolution = (1280, 720)
		camera.framerate = 30
		# Give the camera's auto-exposure and auto-white-balance algorithms
		# some time to measure the scene and determine appropriate values
		camera.iso = 200
		time.sleep(2)
		# Now fix the values
		camera.shutter_speed = camera.exposure_speed
		camera.exposure_mode = 'off'
		g = camera.awb_gains
		camera.awb_mode = 'off'
		camera.awb_gains = g
		# Finally, take several photos with the fixed settings
		if samples > 512 or samples < 0:
			samples = 512
		steps = int(512 /samples*512)
		for s in range(samples- 1):
			camera.capture('ir.jpg')
			s, img = cam.read()
			if s: cv2.imwrite("filename.jpg",img) #save image
			# data = {'ecan':'1', 'weight':get_weight.get()}
			# files = {'pi_im': open('pi_im.jpg', 'rb'),'usb_im':open('usb_im.jpg', 'rb')}
			# url = 'http://127.0.0.1:8000/ecan/upload/'
			# url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'
			# r = requests.post(url, data = data, files=files)
			forward(10, steps)
		cam.release()

# camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
# data = {'ecan':'1', 'weight':get_weight.get()}
# files = {'image_color': open('color.jpg', 'rb'),'image_ir':open('ir.jpg', 'rb')}
# #url = 'http://127.0.0.1:8000/ecan/upload/'
# url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'
# r = requests.post(url, data = data, files=files)
# print r.text
