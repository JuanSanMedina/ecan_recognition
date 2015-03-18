# Functions
import get_weight
from set_stepper import *
from upload_functions import *
import time
import cmd2

# Object identifier
ts = time.time()

# Set GPIOs and url
set_gpio()
url = 'http://128.122.72.105:8000'

# User Interface #
try:

    # Check if gram scale is connected and/or turned on
    while True:
        try:
            print 'Does this weight make sense?'
            print get_weight.get()
            break
        except 'NoneType':
            print "Please connect and turn on the scale"

    # Start process #
    cont = 'y'
    while cont == 'y':

        # Take preview of object #
        # Previews are available at api/site_media/media/sample
        preview = raw_input("Preview? [y/n]")
        if preview == 'y':
            while preview == 'y':
                take = raw_input("Take? [y/n]")
                if take == 'y':
                    get_preview(url)
                preview = raw_input("Keep doing this? [y/n]")

        # Collect data #
        samples = raw_input("Number of samples? [max: 512]")
        item_attributes = {}
        item_attributes['item_class'] = raw_input("What class? ")
        item_attributes['test_train'] = raw_input("Train or test? [1/0]")
        result = get_data(int(samples), item_attributes, url)
        print result
        cont = raw_input("Continue? [y/n] ")
        if cont != 'y' and cont != 'n':
            cont = 'n'
            GPIO.cleanup()

except ValueError:
    GPIO.cleanup()
except KeyboardInterrupt:
    GPIO.cleanup()
