import datetime

import requests
from app.entities import Album


class VkontakteClubManager:
    def __init__(self, key, club_id):
        self.key = key
        self.club_id = club_id
        self.Albums = self.get_albums_from_api()

    def get_albums_from_api(self, limit=50):
        r = requests.get(
            'https://api.vk.com/method/wall.get',
            params={
                'access_token': self.key,
                'v': '5.130',
                'domain': self.club_id,
                'count': limit
            }
        )
        items = r.json()['response']['items']
        result = []
        for item in items:
            item_date = datetime.datetime.utcfromtimestamp(item['date'])
            Albums = {}
            if 'attachments' not in item:
                continue
            for attach in item['attachments']:
                if attach['type'] == 'audio':
                    artist = attach['audio']['artist']
                    title = attach['audio']['title']
                    if attach['audio']['artist'] in Albums:
                        Albums[artist].append(title)
                    else:
                        Albums[artist] = [title]
                else:
                    continue
            if len(Albums.keys()) != 1:
                continue
            for artist, trucks in Albums.items():
                result.append(Album(artist=artist,
                                    trucks=tuple(trucks)))
        return result
