import requests
import datetime

headers = {'X-Yandex-API-Key': '85fe82fd-5e67-4043-9879-5f7a7640916c'}
url = 'https://api.weather.yandex.ru/v1/forecast?lat=55.75396&lon=37.620393'
days = {'0': 'понедельник', '1': 'вторник', '2': 'среда', '3': 'четверг',
        '4': 'пятница', '5': 'суббота', '6': 'воскресенье', }
weather = {'overcast-and-light-rain': 'облачно и легкий-дождь', 'overcast': 'пасмурная погода',
           'clear': 'ясная погода', 'partly-cloudy': 'местами облачно', 'cloudy': 'облачно'}
response = requests.get(url, headers=headers).json()
final_message = ''
for i in response['forecasts']:
    day_number = i['date'].split('-')
    day = datetime.datetime(int(day_number[0]), int(day_number[1]), int(day_number[2]))
    week_day = days[str(day.weekday())]
    night_temp = i['parts']['night']['temp_avg']
    day_temp = i['parts']['day']['temp_avg']
    day_condition = i['parts']['day']['condition']
    day_weather = weather[day_condition]
    final_message += '''
{} ({}):
Днем будет {}
Средняя температура ночью: {}
Средняя температура днем: {}
'''.format(week_day.title(), i['date'], day_weather, night_temp, day_temp)
print(final_message)
print(len(final_message))


'''
tomorrow_forecast = response['forecasts'][1]
night = tomorrow_forecast['parts']['night']
day = tomorrow_forecast['parts']['day']
print(night['temp_avg'], day['temp_avg'])
print(day['condition'])
'''
