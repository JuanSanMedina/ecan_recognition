import io
import requests
import get_weight
from set_stepper import *
import picamera


def outputs(samples, steps, weight, item_class, url):
    global start
    url_item = url + '/ecan/upload/'
    url_bg = url + '/ecan/upload-back_ground/'

    # Take photo of background #
    cont = 'n'
    print 'Prepare for back_ground capture'
    while cont != 'y':
        cont = raw_input("ready? [y] ")
        if cont != 'y':
            cont = 'n'
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
            while cont != 'y':
                cont = raw_input("ready? [y] ")
                if cont != 'y':
                    cont = 'n'
            start = time.time()
        elif i > 3:
            my_file = stream
            data_item = {
                'ecan': '1', 'bg': bg_pk,
                'weight': weight,
                'item_class': item_class}
            files_item = {'im': my_file}
            r = requests.post(
                url_item, data=data_item, files=files_item)
            print r.text
            forward(10, steps)
        stream.truncate(0)
        stream.seek(0)


def get_data(samples, item_class, url):
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
            outputs(samples, steps, weight, item_class, url),
            'jpeg', use_video_port=True)
        finish = time.time()
        print'Captured %s' % samples + ' images in %.2fs' % (finish - start)
    return 'done'


def get_preview(url):
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
        data = {'ecan': '1'}
        files = {'im': open('sample.jpg', 'rb')}
        url_preview = url + '/ecan/upload-sample/'
        r = requests.post(url_preview, data=data, files=files)
        print r
    return 'done'
