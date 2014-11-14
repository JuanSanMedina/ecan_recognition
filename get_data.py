import time
import picamera
# import pygame.camera
# import pygame.image
import get_weight
import requests
import RPi.GPIO as GPIO
import time
import cv2

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

# def take_usb():
# 	pygame.camera.init()
# 	cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
# 	cam.start()
# 	img = cam.get_image()
# 	pygame.image.save(img, "color.jpg")
# 	pygame.camera.quit()

# take_picamera()
# take_usb()

def get_data(samples, item_class):
	
	with picamera.PiCamera() as camera:
		camera.resolution = (1280, 1024)
		camera.iso = 200
		camera.framerate = 30
		time.sleep(2)
		# camera.shutter_speed = camera.exposure_speed
		# camera.exposure_mode = 'off'
		g = camera.awb_gains
		camera.awb_mode = 'off'
		camera.awb_gains = g
		steps = int(512 /samples)
		for s in range(samples):
			print 'juan'
			cam = cv2.VideoCapture(0)	
			cam.set(3,1280)
			cam.set(4,1024)
			camera.capture('pi_cam/pi_cam%s' %s + '.jpg')
			# time.sleep(10/1000.0)
			cam.set
			correct, img = cam.read()
			if correct: cv2.imwrite('usb_cam/usb_cam%s' %s + '.jpg',img) #save image
			# data = {'ecan':'1', 'weight':get_weight.get()}
			# files = {'pi_im': open('pi_im.jpg', 'rb'),'usb_im':open('usb_im.jpg', 'rb')}
			# url = 'http://127.0.0.1:8000/ecan/upload/'
			# url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'
			# r = requests.post(url, data = data, files=files)
			cam.release()
			forward(5, steps)
	return 'done'

cont = 'y'
while cont == 'y':
	samples = raw_input("Number of samples?")
	# item_class = raw_input("What class? ")
	get_data(int(samples), 'erase this')
	cont = raw_input("Continue? [y/n] ")
	if cont != 'y' or cont != 'n':
		cont = 'n'
GPIO.cleanup()


# camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
# data = {'ecan':'1', 'weight':get_weight.get()}
# files = {'image_color': open('color.jpg', 'rb'),'image_ir':open('ir.jpg', 'rb')}
# #url = 'http://127.0.0.1:8000/ecan/upload/'
# url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'
# r = requests.post(url, data = data, files=files)
# print r.text



# camera.resolution = (1280, 720)
# camera.framerate = 30
# # Give the camera's auto-exposure and auto-white-balance algorithms
# # some time to measure the scene and determine appropriate values
# camera.iso = 200
# time.sleep(2)
# # Now fix the values
# camera.shutter_speed = camera.exposure_speed
# camera.exposure_mode = 'off'
# g = camera.awb_gains
# camera.awb_mode = 'off'
# camera.awb_gains = g
# Finally, take several photos with the fixed settings
# if samples > 512 or samples < 0:
# 	samples = 512