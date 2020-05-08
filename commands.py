import sys
from io import BytesIO
from geopy.distance import great_circle
import requests
from PIL import Image

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "85a99676-6991-4b77-a07c-fe0cb368f96f"

# address_ll = "37.588392,55.734036"
address_ll = ','.join(sys.argv[1:])

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)

# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][0]

# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
org_time = organization["properties"]["CompanyMetaData"]['Hours']['text']
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
delta = "0.04"
print('Адресс: {}'.format(org_address))
print('Название: {}'.format(org_name))
print('Время работы: {}'.format(org_time))
print('Расстояние: {}км'.format(great_circle(org_point, address_ll).kilometers))
# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "ll": address_ll,
    "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},pm2dgl~{1},pm2dgl".format(org_point, address_ll)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()
