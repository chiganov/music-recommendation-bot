import requests
import logging

class LastfmManager:
    API_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, key):
        self.key = key

    def get_tags_for_artist(self, artist):
        r = requests.post(
            self.API_URL,
            params={
                "method": "artist.getTopTags",
                "api_key": self.key,
                "artist": artist,
                "format": "json",
            },
        )
        data = r.json()
        if not 'toptags' in data:
            logging.warning(f"Can't get tags: {r.json()}")
            return []
        return [tag["name"] for tag in data["toptags"]["tag"]]

    def get_tags_for_albom(self, artist, album):
        r = requests.post(
            self.API_URL,
            params={
                "method": "album.getTopTags",
                "api_key": self.key,
                "artist": artist,
                "album": album,
                "format": "json",
            },
        )
        data = r.json()
        if not 'toptags' in data:
            logging.warning(f"Can't get tags: {r.json()}")
            return []
        return [tag["name"] for tag in data["toptags"]["tag"]]
