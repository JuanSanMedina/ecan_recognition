import time
import picamera
import pygame.camera
import pygame.image
import get_weight
import requests

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

data = {'ecan':'1', 'weight':get_weight.get()}
files = {'image_color': open('color.jpg', 'rb'),'image_ir':open('ir.jpg', 'rb')}
#url = 'http://127.0.0.1:8000/ecan/upload/'
url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'
r = requests.post(url, data = data, files=files)
print r.text
