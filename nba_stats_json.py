import urllib
import json

url = ''

response = urllib.urlopen(url)
data = json.loads(response.read())

print data['results'][0]
