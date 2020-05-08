import sys
from io import BytesIO
import requests
from PIL import Image

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

# address_ll = "37.588392,55.734036"
# 45.168183,53.193330 (координаты Заречного)
address_ll = ','.join(sys.argv[1:])

search_params = {
    "apikey": api_key,
    "text": "больница",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
json_response = response.json()
marks = ''
print(len(json_response["features"]))
for i in range(10):
    organization = json_response["features"][i]
    #  org_time = organization["properties"]["CompanyMetaData"]['Hours']['text']
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    marks += '{},pm2gnl~'.format(org_point)
marks = marks[:-1]
delta = "0.05"
map_params = {
    "ll": address_ll,
    "spn": ",".join([delta, delta]),
    "l": "map",
    "pt": marks
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()
