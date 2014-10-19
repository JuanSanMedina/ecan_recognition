
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
# url = 'http://127.0.0.1:8000/ecan/upload-ecan/'
	
def send(ip):	
	url = 'http://ecan-recognition.herokuapp.com/ecan/upload-ecan/'
	data = {'pk':'1', 'address':'CUSP', 'latitude':3.0, 'longitude':2.0, 'ip': ip}
	r = requests.post(url, data = data)
	print r.text

send(sys.argv[1])
