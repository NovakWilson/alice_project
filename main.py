from flask import Flask, request
from math import sin, cos, sqrt, atan2, radians
import logging
import json
import os
import requests

app = Flask(__name__)

#logging.basicConfig(level=logging.INFO)
search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "85a99676-6991-4b77-a07c-fe0cb368f96f"
OAuth = 'AgAAAAAqf_iLAAT7o_EKmn5n1kmmvwSwyWpHM_I'
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    #logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    #logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'is_address': False,
            'cords_from': ''
        }
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Я могу найти любой ближайший к вам объект, для этого ' \
                            'введите свой адрес'
    else:
        if not sessionStorage[user_id]['is_address']:
            address = req['request']['original_utterance']
            cords_from = get_coordinates(address)
            if cords_from is None:
                res['response']['text'] = 'Мы не смогли вас найти. Возможно адресс задан некорректно. ' \
                                          'Попробуйте еще раз.'
                return
            sessionStorage[user_id]['is_address'] = True
            sessionStorage[user_id]['cords_from'] = cords_from
            res['response']['text'] = '''Вы можете: 
                                      1) Найти любой ближайший объект в вашем городе (аптека, больница, автосалон).
                                      Для этого введите: найти объект <сам объект>
                                      2) Найти расстояние между двумя городами.
                                      Для этого введите: найти расстояние <город1> <город2>
                                      3) Определить страну, в которой находится введенный город.
                                      Для этого введите: в какой стране <город>'''
        else:
            x_cord = sessionStorage[user_id]['cords_from'][0]
            y_cord = sessionStorage[user_id]['cords_from'][1]
            address_ll = '{},{}'.format(x_cord, y_cord)
            tokens = req['request']['nlu']['tokens']
            if tokens[0] == 'найти' and tokens[1] == 'объект':
                search_params = {
                    "apikey": api_key,
                    "text": tokens[2:],
                    "lang": "ru_RU",
                    "ll": address_ll,
                    "type": "biz"
                }
                try:
                    response = requests.get(search_api_server, params=search_params)
                    json_response = response.json()
                    try:
                        organization = json_response["features"][0]
                    except:
                        res['response']['text'] = 'К сожалению Яндекс заблокировал нам доступ к своему справочнику, ' \
                                                  'но Вы можете посмотреть на город с карты. '
                        map_request = "http://static-maps.yandex.ru/1.x/?ll={}&spn=0.1,0.1&l=sat".format(address_ll)
                        response = requests.get(map_request)
                        map_file = "/map.png"
                        with open(map_file, "wb") as file:
                            file.write(response.content)
                        return
                    org_name = organization["properties"]["CompanyMetaData"]["name"]
                    try:
                        org_time = organization["properties"]["CompanyMetaData"]['Hours']['text']
                    except:
                        org_time = 'Не указанно'
                    sessionStorage[user_id]['org'] = organization["properties"]["CompanyMetaData"]
                    sessionStorage[user_id]['buttons'] = [
                        {
                            'title': 'Показать время работы',
                            'hide': True
                        },
                        {
                            'title': 'Показать на карте',
                            'hide': True
                        }
                    ]
                    org_address = organization["properties"]["CompanyMetaData"]["address"]
                    res['response']['text'] = '''
                                              Адресс: {}.
                                              Название: {}
                                              '''.format(org_address, org_name)
                    res['response']['buttons'] = [
                        {
                            'title': 'Показать время работы',
                            'hide': True
                        },
                        {
                            'title': 'Показать на карте',
                            'hide': True
                        }
                    ]
                except:
                    res['response']['text'] = 'Не могу найти данный объект. Возможно он не обозначен или ' \
                                              'ввод не соответствует требованиям.'

            elif tokens[0] in ['найти', 'найди'] and tokens[1] == 'расстояние':
                try:
                    city1 = tokens[-2]
                    city2 = tokens[-1]
                    distance = get_distance(get_coordinates(city1), get_coordinates(city2))
                    res['response']['text'] = 'Расстояние между этими городами: ' + \
                              str(round(distance)) + ' км.'
                except:
                    res['response']['text'] = 'Не могу найти данные Города. Возможно ' \
                          'ввод не соответствует требованиям.'

            elif tokens[0] == 'в' and tokens[1] == 'какой' and tokens[2] == 'стране':
                try:
                    country = get_country(tokens[-1])
                    res['response']['text'] = 'Страна города {}: {}'.format(tokens[-1], country)
                except:
                    res['response']['text'] = 'Не могу найти страну. Возможно ввод не соответствует требованиям.'

            elif req['request']['original_utterance'].lower() == 'показать время работы':
                try:
                    work_time = sessionStorage[user_id]['org']['Hours']['text']
                except:
                    work_time = 'Не указано'
                res['response']['text'] = 'Время работы: {}'.format(work_time)
                sessionStorage[user_id]['buttons'] = [i for i in sessionStorage[user_id]['buttons'] if not i['title'] == 'Показать время работы']
                res['response']['buttons'] = sessionStorage[user_id]['buttons']
                return

            elif req['request']['original_utterance'].lower() == 'показать на карте':
                cords_to = get_coordinates(sessionStorage[user_id]['org']["address"])
                #  map_request = "http://static-maps.yandex.ru/1.x/?ll={}&spn=0.1,0.1&l=map".format(cords_to)
                json = {"url": "http://static-maps.yandex.ru/1.x/?ll={}&z=15&l=map".format(','.join([str(i) for i in cords_to]))}
                print(json)
                headers = {'Authorization': 'OAuth AgAAAAAqf_iLAAT7o_EKmn5n1kmmvwSwyWpHM_I'}
                url = 'https://dialogs.yandex.net/api/v1/skills/f014ed35-b7ff-4b51-969e-690abc790540/images'
                response = requests.post(url, json=json, headers=headers).json()
                print(response)
                image_id = response['image']['id']
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = sessionStorage[user_id]['org']['name']
                res['response']['card']['image_id'] = image_id
                res['response']['text'] = sessionStorage[user_id]['org']['address']
                sessionStorage[user_id]['buttons'] = [i for i in sessionStorage[user_id]['buttons'] if not i['title'] == 'Показать на карте']
                res['response']['buttons'] = sessionStorage[user_id]['buttons']
                '''
                headers = {'Authorization': 'OAuth AgAAAAAqf_iLAAT7o_EKmn5n1kmmvwSwyWpHM_I'}
                url = 'https://dialogs.yandex.net/api/v1/skills/f014ed35-b7ff-4b51-969e-690abc790540/images/{}'.format(image_id)
                requests.delete(url, headers=headers)
                '''
                return
            else:
                res['response']['text'] = '''Кроме этих команд я ничего не понимаю. Пока, что.
                          1) Найти любой ближайший объект в вашем городе (аптека, больница, автосалон).
                          Для этого введите: найти объект <сам объект>
                          2) Найти расстояние между двумя городами.
                          Для этого введите: найти расстояние <город1> <город2>
                          3) Определить страну, в которой находится введенный город.
                          Для этого введите: в какой стране <город>'''


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


def get_coordinates(city_name):
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        'geocode': city_name,
        'format': 'json'
    }
    response = requests.get(url, params)
    json = response.json()
    if json['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == '0':
        return None
    coordinates_str = json['response']['GeoObjectCollection'][
        'featureMember'][0]['GeoObject']['Point']['pos']
    return list(map(float, coordinates_str.split()))


def get_distance(p1, p2):

    R = 6373.0

    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


def get_country(city):

    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b'
    }

    response = requests.get(url, params)
    json = response.json()

    return json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
