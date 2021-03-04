import datetime

import requests
from app.entities import Albom


class VkontakteClubManager:
    def __init__(self, key, club_id):
        self.key = key
        self.club_id = club_id
        self.alboms = self.get_albums_from_api()

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
            alboms = {}
            if 'attachments' not in item:
                continue
            for attach in item['attachments']:
                if attach['type'] == 'audio':
                    artist = attach['audio']['artist']
                    title = attach['audio']['title']
                    if attach['audio']['artist'] in alboms:
                        alboms[artist].append(title)
                    else:
                        alboms[artist] = [title]
                else:
                    continue
            if len(alboms.keys()) != 1:
                continue
            for artist, traks in alboms.items():
                result.append(Albom(artist=artist,
                                    traks=tuple(traks)))
        return result
