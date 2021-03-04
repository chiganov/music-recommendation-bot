import requests
import datetime
import logging


class SpotifyManager:
    def __init__(self, key, client_id):
        self.key = key
        self.client_id = client_id
        self._access_token = None
        self._access_token_expiration_time = None

    def _get_access_token(self):
        if self._access_token and self._access_token_expiration_time:
            if self._access_token_expiration_time > datetime.datetime.now():
                return self._access_token
        r = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.key,

            },
        )
        data = r.json()
        self._access_token = data['access_token']
        self._access_token_expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
        return self._access_token

    def get_artist_id_by_name(self, name):
        r = requests.get(
            'https://api.spotify.com/v1/search',
            params={
                'q': name,
                'type': 'artist',
                'access_token': self._get_access_token()
            },
        )
        data = r.json()
        if not data['artists']['items']:
            return None
        data = data['artists']['items'][0]
        if data['name'] != name:
            return
        return data['id']

    def get_albums_ids_by_artist_id(self, artist_id):
        flag = True
        step = 50
        offset = 0
        access_token = self._get_access_token()
        result = []
        while flag:
            data = []
            r = requests.get(
                f'https://api.spotify.com/v1/artists/{artist_id}/albums',
                params={
                    'offset': offset,
                    'limit': step,
                    'access_token': access_token,
                },
            )
            data = r.json()
            if 'items' not in data:
                logging.error(f'Spotify API error: {data}')
                raise KeyError('items')
            data = [item['id'] for item in data['items']]
            if data:
                result += data
                offset += step
            else:
                flag = False
        return result

    def get_trak_names_for_album_id(self, album_id):
        flag = True
        step = 50
        offset = 0
        result = []
        access_token = self._get_access_token()
        while flag:
            data = []
            r = requests.get(
                f'https://api.spotify.com/v1/albums/{album_id}/tracks',
                params={
                    'offset': offset,
                    'limit': step,
                    'access_token': access_token,
                },
            )
            data = r.json()
            if 'items' not in data:
                logging.error(f'Spotify API error: {data}')
                raise KeyError('items')
            data = [item['name'] for item in data['items']]
            if data:
                result += data
                offset += step
            else:
                flag = False
        return result
