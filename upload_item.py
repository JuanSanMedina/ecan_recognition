import requests
# from pprint import pprint

url = 'http://127.0.0.1:8000/ecan/upload/'
# url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'

data = {'ecan':'1', 'weight':'12', 'item_class':'1'}
files = {'image_picam': open('pi.jpg', 'rb')}

r = requests.post(url, data = data, files=files)
print r.text