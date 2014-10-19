import requests
# from pprint import pprint
url = 'http://127.0.0.1:8000/ecan/view-ip/'
#url = 'http://ecan-recognition.herokuapp.com/ecan/view-ip/'
data = {'pk':'1'}
r = requests.get(url, params = data)
print r.text