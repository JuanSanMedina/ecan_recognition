
"""Defines a CLI to obtain images of an object on a rotating platform."""

from termcolor import colored
import cmd2
import io
import math
import picamera
import readline
import requests
import RPi.GPIO as GPIO
import socket
import stepper
import time
import usb
import weight


def get_weight():
    """Get weight of USB scale."""
    VENDOR_ID = 0x0922
    PRODUCT_ID = 0x8004

    # find the USB device
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device.is_kernel_driver_active(0): device.detach_kernel_driver(0)

    # use the first/default configuration
    device.set_configuration()

    # first endpoint
    endpoint = device[0][(0, 0)][0]

    # read a data packet
    attempts = 10
    data = None

    while data is None and attempts > 0:
        try:
            data = \
                device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                attempts -= 1
                continue

    raw_weight = data[4] + data[5] * 256
    device.detach_kernel_driver(0)
    return float(raw_weight)


def upload_images(samples, steps, item_attributes, url):
    """Upload images from object."""
    global start
    url_item = url + '/ecan/upload/'
    url_bg = url + '/ecan/upload-back_ground/'

    # Take photo of background #
    cont = 'n'
    print 'Prepare for back_ground capture'

    while cont != '1':
        cont = raw_input("ready? [1] ")
        if cont != '1':
            cont = 'n'

    # Start Camara Streaming #
    stream = io.BytesIO()
    for i in range(samples + 4):
        yield stream
        stream.seek(0)
        if i == 0:
            my_file_bg = stream
            data_bg = {'ecan': '1'}
            files_bg = {'im': my_file_bg}
            r = requests.post(url_bg, data=data_bg, files=files_bg)
            if r.json()['result'] == 'valid':
                bg_pk = r.json()['id']
                print r.json()['result'], 'back_ground id: ', r.json()['id']
            else:
                print 'Operation not completed'

            # Place Item and upload data #
            print 'Place item'
            cont = 'n'
            while cont != '1':
                cont = raw_input("ready? [1] ")
                if cont == '1':
                    item_attributes['weight'] = get_weight()
                if cont != '1':
                    cont = 'n'
            start = time.time()
        elif i > 3:
            my_file = stream
            item_attributes['bg'] = bg_pk
            item_attributes['ecan'] = '1'
            data_item = item_attributes
            files_item = {'im': my_file}
            r = requests.post(
                url_item, data=data_item, files=files_item)
            print r.text
            stepper.forward(20, steps)
        stream.truncate(0)
        stream.seek(0)


def get_data(samples, item_attributes, url):
    """Get images for currect object."""
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

        # Record Data #
        steps = int(math.ceil(512. / samples))
        camera.capture_sequence(
            upload_images(samples, steps, item_attributes, url),
            'jpeg', use_video_port=True)
        finish = time.time()
        print'Captured %s' % samples + ' images in %.2fs' % (finish - start)

    return "done"


def get_preview(url):
    """Get preview of current image."""
    with picamera.PiCamera() as camera:
        camera.led = False
        camera.resolution = (1024, 768)
        camera.iso = 200
        camera.framerate = 10
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        camera.capture('sample.jpg')
        data = {'ecan': '1'}
        files = {'im': open('sample.jpg', 'rb')}
        url_preview = url + '/ecan/upload-sample/'
        r = requests.post(url_preview, data=data, files=files)
        print r.text

    return "done"


def predict(url):
    """Take picture and predict class."""
    with picamera.PiCamera() as camera:
        camera.led = False
        camera.resolution = (1024, 768)
        camera.iso = 200
        camera.framerate = 10
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        camera.capture('sample.jpg')
        data = {'ecan': '1'}
        files = {'im': open('sample.jpg', 'rb')}
        url_preview = url + '/ecan/predict/'
        r = requests.post(url_preview, data=data, files=files)
        print(r.text)

    return "done"


class EcanInterface(cmd2.Cmd):

    """Ecan Command Line Interface Application."""

    # Set GPIOs and url
    url = 'http://128.122.72.105:8000'

    # Class variables
    ATT_KEYS = ['logo', 'shape', 'material', 'common_name']
    ATT_DICT = dict.fromkeys(ATT_KEYS)

    # Update ATT_DICT
    for k in ATT_KEYS:
        data = {'action': 'view', 'att_key': k}
        d = requests.post(url + '/ecan/insert/', data).json()
        ATT_DICT[k] = eval(d['dictionary'])

    # Uploaded items in session
    UP_IT = {}

    @cmd2.options([
        cmd2.make_option(
            '-v', '--view', action="store_true", help="view current values."
            )
        ])
    def do_insert(self, arg, opts=None):
        """
        Insert a new item attribute to database.

        Keyword arguments:
        logo -- add new logo (default 0.0)
        shape -- add new shape (default 0.0)
        material -- add new material (default 0.0)
        """
        if not arg or arg not in self.ATT_KEYS:
            print colored('Error: ', 'red') + \
                'please insert a valid argument [help insert]'
            return

        self.update_attributes()
        values_print = [colored(e, 'blue', attrs=['bold'])
                        for e in self.ATT_DICT[arg].keys()]

        if opts.view:
            print '\t'.join(str(e) for e in values_print)
            return

        print '\nCurrent %ss:' % arg
        print '\t'.join(str(e) for e in values_print)

        while True:
            self.upload_insert(arg=arg)
            color_arg = colored(arg, 'blue', attrs=['bold'])
            ans = self.select(['yes', 'no'],
                              'Add other %s?: ' % color_arg)
            if ans == 'no':
                break
                return

    def do_upload(self, arg):
        """Data collection function."""
        same_package = False

        try:
            # Start process
            while True:
                # Initialize item dictionary
                keys = ['weight', 'identifier', 'common_name', 'shape',
                        'material', 'logo', 'transparency']
                item_att = dict.fromkeys(keys)

                # Take preview of object
                # Previews are available at api/site_media/media/sample
                ans = self.select(['yes', 'no'], "Take preview?: ")
                if ans == 'yes':
                    self.do_take_preview()

                # Get attributes
                keys = self.ATT_KEYS
                pos = 0
                while True:
                    try:
                        ans = self.get_attributes(keys[pos])
                        if ans == colored('go back', 'blue'):
                            if pos == 0:
                                pos = 0
                            else:
                                pos -= 1
                        else:
                            item_att[keys[pos]] = ans
                            pos += 1
                    except IndexError:
                        break

                # Ask for transparency
                item_att['transparency'] = \
                    self.select(['yes', 'no'], "Is it transparent?: ")

                # Run data collection
                while True:
                    # Set item identifier
                    item_att['identifier'] = '%.2f' % time.time()
                    # Check if gram scale and collect weight
                    if not same_package:
                        self.do_get_weight('return')
                        # Select number of samples
                        samples = self.select(['90', '180', '360'],
                                              'Select number of samples: ')

                    # Confirm data package
                    print '\nData package:'
                    print item_att
                    print 'Number of samples %s\n' % samples
                    attention = colored('Atention! ', 'yellow', attrs=['bold'])
                    ans = self.select(['yes', 'no'],
                                      attention + 'Confirm data-package?: ')
                    if ans == 'yes':
                        result = get_data(int(samples), item_att, self.url)
                        self.UP_IT[item_att['identifier']] = 1
                        print result

                    # delete previous?
                    ans = self.select(['yes', 'no'],
                                      'keep previous?: ')
                    if ans == 'no':
                        self.do_delete_object(item_att['identifier'])

                    # Run with same data_package?
                    ans = self.select(['yes', 'no', 'yes, but change field'],
                                      'Run again with same attributes?: ')
                    if ans == 'no':
                        same_package = False
                        break
                    elif ans == 'yes, but change field':
                        same_package = True
                        while True:
                            ans = self.select(
                                ['end'] + self.ATT_KEYS, 'what field?: ')

                            if ans == 'end':
                                break
                            else:
                                value = self.get_attributes(ans)
                                if value == colored('go back', 'blue'):
                                    pass
                                else:
                                    item_att[ans] = value

                    elif ans == 'yes':
                        same_package = True

                # Csontinue data collection?
                ans = self.select(['yes', 'no'], 'Continue data collection?: ')
                if ans == 'yes':
                    pass
                else:
                    readline.set_completer(self.complete)
                    break

        except Exception:
            readline.set_completer(self.complete)

    def do_take_preview(self, arg=None):
        """Run to take an ecan preview."""
        while True:
            ans = self.select(['yes', 'no'], "Take?: ")
            if ans == 'yes':
                get_preview(self.url)
            elif ans == 'no':
                break

    def do_delete_object(self, arg=None):
        """Run to take an ecan preview."""
        if arg:
            data = {'identifier': arg}
            r = requests.get(self.url + '/ecan/delete_object/',
                             params=data)
            print r.json()['result']
        else:
            while True:
                keys = self.UP_IT.keys()
                keys.sort(key=float)
                identifier = self.select(keys,
                                         "Select object to delete: ")
                ans = self.select(['yes', 'no'], "Continue?: ")
                if ans == 'yes':
                    data = {'identifier': identifier}
                    r = requests.get(self.url + '/ecan/delete_object/',
                                     params=data)
                    print r.json()['result']
                    if r.json()['result'] == 'valid':
                        self.UP_IT.pop(identifier, None)
                elif ans == 'no':
                    break

    def upload_insert(self, arg):
        """Ask for new value."""
        while True:
            ans = raw_input('\nEnter %s: ' % arg).lower().replace(' ', '_')
            cont = self.select(['yes', 'no'],
                               "Proceed?: ")
            if cont == 'yes' and ans not in self.ATT_DICT[arg].keys():
                break
            elif cont == 'no':
                return
            elif ans not in self.ATT_DICT[arg].keys():
                print arg + ' already exists'

        # Upload new attribute
        data = {'att_key': arg, 'action': 'save', 'value': ans}
        r = requests.post(self.url + '/ecan/insert/', data=data).json()
        d = eval(r['dictionary'])
        print '*** %s: succesfully added*** ' \
            % colored(r['result'], 'green')
        self.ATT_DICT[arg][ans] = d[ans]
        print '\nUpdated %ss: ' % arg
        print '\t'.join(colored(e, 'green',
                                attrs=['bold']) for e in d.keys())

    def do_get_weight(self, arg=None):
        """Get weight."""
        while True:
            try:
                w = get_weight()
                print '\nCurrent weight %s:' % \
                    colored(w, 'blue', attrs=['bold'])
                ans = self.select(['yes', 'no'],
                                  "does this weight make sense?: ")
                if ans == 'yes':
                    if arg is None:
                        return
                    if arg is 'return':
                        return w
                    break
            except AttributeError:
                print "Please connect and turn on the scale"
                ans = self.select(['yes', 'no'],
                                  "ready?: ")
                if ans == 'no':
                    break

    def get_attributes(self, k):
        """Get attributes."""
        print '\nInsert %s:' % colored(k, 'blue', attrs=['bold'])
        while True:
            completer = self.Completer(['1', '2', '3'])
            readline.set_completer(completer.complete)
            opts = [colored(e, 'blue')
                    for e in ['insert new', 'go back']]
            ans = self.select(opts +
                              self.ATT_DICT[k].keys(),
                              'Please select one option: ')
            if ans == colored('insert new', 'blue'):
                self.do_insert(k)
            elif ans == 'go back':
                value = ans
                break
            else:
                value = self.ATT_DICT[k][ans]
                break
        return value

    def update_attributes(self):
        """Update database attributes."""
        for k in self.ATT_KEYS:
            data = {'action': 'view', 'att_key': k}
            d = requests.post(self.url + '/ecan/insert/', data).json()
            self.ATT_DICT[k] = eval(d['dictionary'])

    def complete_insert(self, text, line, begidx, endidx):
        """Complete insert."""
        if not text:
            completions = self.ATT_KEYS
        else:
            completions = [f
                           for f in self.ATT_KEYS
                           if f.startswith(text)
                           ]
        return completions

    class Completer:

        """I have no clue what I did this for."""

        def __init__(self, completions):
            self.completions = completions

        def complete(self, text, state):
            for word in self.completions:
                if word.startswith(text):
                    if not state:
                        return word
                    else:
                        state -= 1

    def select(self, options, prompt='Your choice? '):
        """
        Present a numbered menu to the user.

        Modelled after the bash shell's SELECT.  Returns the item chosen.

        Argument ``options`` can be:

         | a single string -> will be split into one-word options
         | a list of strings -> will be offered as options
         | a list of tuples -> interpreted as (value, text), so
                               that the return value can differ from
                               the text advertised to the user
        """
        if isinstance(options, basestring):
            options = zip(options.split(), options.split())
        fulloptions = []
        for opt in options:
            if isinstance(opt, basestring):
                fulloptions.append((opt, opt))
            else:
                try:
                    fulloptions.append((opt[0], opt[1]))
                except IndexError:
                    fulloptions.append((opt[0], opt[0]))
        flag = True
        for (idx, (value, text)) in enumerate(fulloptions):
            if flag:
                self.poutput('\n  %2d. %s\n' % (idx + 1, text))
                flag = False
            else:
                self.poutput('  %2d. %s\n' % (idx + 1, text))
        while True:
            response = raw_input(prompt)
            try:
                response = int(response)
                result = fulloptions[response - 1][0]
                break
            except ValueError:
                pass  # loop and ask again
        return result


if __name__ == '__main__':

    stepper.set_gpio()
    EcanInterface().cmdloop()
    GPIO.cleanup()
