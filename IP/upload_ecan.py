import requests
import sys
	
def send(ip):
   """Update IP of Raspberry PI in server."""
   url = 'http://ecan-recognition.herokuapp.com/ecan/upload-ecan/'
   data = {'pk':'1', 'address':'CUSP at PPP', 'latitude':1.0, 'longitude':1.0, 'ip': ip}
   r = requests.post(url, data = data)
   print(r.text)

send(sys.argv[1])
