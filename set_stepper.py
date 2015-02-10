import RPi.GPIO as GPIO
import time


def set_gpio():
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
    delay = int(delay) / 1000.0
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
    delay = int(delay) / 1000.0
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
    coil_A_1_pin = 4
    coil_A_2_pin = 17
    coil_B_1_pin = 27
    coil_B_2_pin = 22
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)
