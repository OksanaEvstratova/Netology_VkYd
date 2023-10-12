import requests
import json
import datetime
from collections import Counter
from tqdm import tqdm

class YandexAPIclient:

    base_ya_url = 'https://cloud-api.yandex.net/'

    def __init__(self, token):
        self.headers = {
            'Authorization': token
        }
    def create_folder(self, folder_name):

        new_folder_url = self.base_ya_url + 'v1/disk/resources'
        ya_params = {'path': folder_name}
        response = requests.put(new_folder_url, headers=self.headers, params=ya_params)


    def upload_photos(self, items_list, photos_quantity):

        get_link = self.base_ya_url + 'v1/disk/resources/upload'
        likes_set = Counter([d['likes'] for d in items_list])
        result = []

        for item in tqdm(items_list[0:photos_quantity], colour='blue', desc='Progress'):
            link = item['url']

            # формируем имя по лайкам и дате
            if likes_set[item['likes']] == 1:
                file_name = f"{item['likes']}.jpg"
            else:
                file_name = f"{item['likes']}_{item['date']}.jpg"

            params = {'path': f'{folder_name}/{file_name}',
                      'url': link}
            response = requests.post(get_link, params=params, headers=self.headers)
            if response.status_code < 300:
                result.append({'file_name': file_name, 'size': item['size']})

        return result

class VKAPIclient:

    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_profile_photos(self):

        params = {'access_token': self.token,
                       'v': '5.131',
                       'owner_id': self.user_id,
                       'album_id': 'profile',
                       'extended': 1,
                       'photo_sizes': 1}

        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        return response.json()


with open('json_params.json', encoding='utf-8', mode='r') as f_json_params:
    params = json.load(f_json_params)
    token = params['TOKEN']
    ya_token = f"OAuth {params['YA_TOKEN']}"
    user_id = int(params['vk_id'])

# VK
vk_client = VKAPIclient(token, user_id)
# получаем фото профиля
data_photos = vk_client.get_profile_photos()

# обработка результата с ВК
items_list = []
for f in data_photos['response']['items']:
    x =datetime.datetime.date(datetime.datetime.fromtimestamp(int(f['date'])))
    items_list.append({'date': str(x),
                       'likes': f['likes']['count'],
                       'size': f['sizes'][len(f['sizes'])-1]['type'],
                       'url': f['sizes'][len(f['sizes'])-1]['url']})

items_list = sorted(items_list, key=lambda x: x.get('size'), reverse=True)

# Yandex
folder_name = 'VKphotos'
ya_client = YandexAPIclient(ya_token)
# создаем папку
ya_client.create_folder(folder_name)
# загружаем файлы по ссылкам
photos_quantity = min(len(items_list), 5)
result = ya_client.upload_photos(items_list, photos_quantity)

# пишем результат загрузки в файл
with open('result.json', encoding='utf-8', mode='w') as f_json:
    json.dump(result, f_json, ensure_ascii=False, indent=4)

