import requests
# from pprint import pprint
from socket import socket, SOCK_DGRAM, AF_INET 

s = socket(AF_INET, SOCK_DGRAM) 
s.connect(('google.com', 0)) 
ip = str(s.getsockname()[0]) 

# url = 'http://127.0.0.1:8000/ecan/upload-ecan/'
# # url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'

# data = {'pk':'1', 'address':'1', 'latitude':2.0, 'longitude':2.0, 'ip': ip}

# r = requests.post(url, data = data)
# print r.text