import requests

json = {"url": "http://static-maps.yandex.ru/1.x/?ll=50,50&z=3&l=map"}
headers = {'Authorization': 'OAuth AgAAAAAqf_iLAAT7o_EKmn5n1kmmvwSwyWpHM_I'}
url = 'https://dialogs.yandex.net/api/v1/skills/f014ed35-b7ff-4b51-969e-690abc790540/images'
response = requests.post(url, json=json, headers=headers)
print(response.json())
