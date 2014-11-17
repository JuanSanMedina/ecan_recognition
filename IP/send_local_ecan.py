import requests
import sys

# import socket
# from pprint import pprint
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("goolge.com",0))
# ip = str(s.getsockname()[0])
# s.close()
# print ip
# ip = str(socket.gethostbyname(socket.gethostname()))
# from pprint import pprint

def send(ip):	
	url = 'http://127.0.0.1:8000/ecan/upload-ecan/'
	data = {'pk':'1', 'address':'CUSP at PPP', 'latitude':1.0, 'longitude':1.0, 'ip': ip}
	r = requests.post(url, data = data)
	print r.text

send('128.122.72.106')
