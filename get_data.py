import time
import picamera
import pygame.camera
import pygame.image

def take_ir():
	with picamera.PiCamera() as camera:
		camera.start_preview()
		time.sleep(1)
		camera.capture('ir_test.jpg')
		camera.stop_preview()

def take_color():
	pygame.camera.init()
	cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
	cam.start()
	img = cam.get_image()
	pygame.image.save(img, "color_test.jpg")
	pygame.camera.quit()

take_ir()
take_color()
