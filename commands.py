import requests

headers = {'X-Yandex-API-Key': '85fe82fd-5e67-4043-9879-5f7a7640916c'}
url = 'https://api.weather.yandex.ru/v1/forecast?lat=55.75396&lon=37.620393'
response = requests.get(url, headers=headers).json()
tomorrow_forecast = response['forecasts'][1]
print(tomorrow_forecast['parts']['night']['temp_avg'])
print(tomorrow_forecast['parts']['day']['temp_avg'])
