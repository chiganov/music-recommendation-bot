import datetime

import requests
from app.entities import Album


class VkontakteClubManager:
    def __init__(self, key, club_id):
        self.key = key
        self.club_id = club_id
        self.albums = self.get_albums_from_api()

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
            albums = {}
            if 'attachments' not in item:
                continue
            for attach in item['attachments']:
                if attach['type'] == 'audio':
                    artist = attach['audio']['artist']
                    title = attach['audio']['title']
                    if attach['audio']['artist'] in albums:
                        albums[artist].append(title)
                    else:
                        albums[artist] = [title]
                else:
                    continue
            if len(albums.keys()) != 1:
                continue
            for artist, trucks in albums.items():
                result.append(Album(artist=artist,
                                    trucks=tuple(trucks)))
        return result
