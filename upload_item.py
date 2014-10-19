import requests
# from pprint import pprint

#url = 'http://127.0.0.1:8000/ecan/upload/'
url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'

data = {'ecan':'1', 'weight':'2.3'}
files = {'image_color': open('can.jpeg', 'rb'),'image_ir':open('ir_can.jpg', 'rb')}

r = requests.post(url, data = data, files=files)
print r.text