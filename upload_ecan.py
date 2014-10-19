import requests
import socket
# from pprint import pprint

print socket.gethostname()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("gmail.com",80))
print(s.getsockname()[0])
s.close()

# ip = str(socket.gethostbyname(socket.gethostname()))
# url = 'http://127.0.0.1:8000/ecan/upload-ecan/'
# # url = 'http://ecan-recognition.herokuapp.com/ecan/upload/'

# data = {'pk':'1', 'address':'1', 'latitude':2.0, 'longitude':2.0, 'ip': ip}

# r = requests.post(url, data = data)
# print r.text