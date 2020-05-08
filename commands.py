import requests


def get_coordinates(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': city_name,
            'format': 'json'
        }
        response = requests.get(url, params)
        json = response.json()
        coordinates_str = json['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        return list(map(float, coordinates_str.split()))
    except Exception as e:
        return e

'''
import http.client
conn = http.client.HTTPConnection("ifconfig.me")
conn.request("GET", "/ip")
print(conn.getresponse().read())

......

print(socket.gethostbyname(socket.gethostname()))
print(geocoder.ip('192.168.1.251'))

.........

import geocoder
g = geocoder.ip('me')
print(g.latlng)
print(g.ip)
print(geocoder.ip('82.209.124.82').latlng)

.................................

import socket
socket.gethostbyname(socket.gethostname())
'''
