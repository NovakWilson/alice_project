from flask import Flask, request
import logging
import json
import random
import os
import requests

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'is_city': False,
            'city': ''
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
                          + '. Я - Алиса. Введите название города, в котором вы сейчас находитесь'
    else:
        if not sessionStorage[user_id]['is_city']:
            city = get_city(req)
            if city is None:
                res['response']['text'] = 'Не расслышала город. Повтори, пожалуйста!'
            else:
                sessionStorage[user_id]['is_city'] = True
                sessionStorage[user_id]['city'] = city
                res['response']['text'] = 'Вы можете найти любой ближайший объект в вашем городе (аптека, больница, автосалон). ' \
                    'Для этого введите: найти объект <сам объект>'
        else:
            x_cord = get_coordinates(sessionStorage[user_id]['city'])[0]
            y_cord = get_coordinates(sessionStorage[user_id]['city'])[1]
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
                    organization = json_response["features"][0]
                    org_name = organization["properties"]["CompanyMetaData"]["name"]
                    try:
                        org_time = organization["properties"]["CompanyMetaData"]['Hours']['text']
                    except:
                        org_time = 'Не указанно'
                    org_address = organization["properties"]["CompanyMetaData"]["address"]
                    res['response']['text'] = '''
                                              Адресс: {}.
                                              Название: {}
                                              Время работы: {}
                                              '''.format(org_address, org_name, org_time)
                except:
                    res['response']['text'] = 'Не могу найти данный объект. Возможно он не обозначен или ' \
                                              'ввод не соответствует требованиям.'


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
    coordinates_str = json['response']['GeoObjectCollection'][
        'featureMember'][0]['GeoObject']['Point']['pos']
    return list(map(float, coordinates_str.split()))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
