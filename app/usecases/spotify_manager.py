import requests
import datetime
import logging
import time


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
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.key,
            },
        )
        data = r.json()
        self._access_token = data["access_token"]
        self._access_token_expiration_time = (
            datetime.datetime.now() + datetime.timedelta(seconds=data["expires_in"])
        )
        return self._access_token

    def get_artist_id_by_name(self, name):
        while True:
            r = requests.get(
                "https://api.spotify.com/v1/search",
                params={
                    "q": name,
                    "type": "artist",
                    "access_token": self._get_access_token(),
                },
            )
            data = r.json()
            if "error" in data and data["error"].get("status") == 429:
                wait_for_time = int(r.headers["Retry-After"]) + 2
                logging.info(f"Spotify Retry-After: {wait_for_time}")
                time.sleep(wait_for_time)
                continue
            break
        for data in data["artists"].get("items", []):
            if data["name"] == name:
                return data["id"]
        return None

    def get_albums_ids_by_artist_id(self, artist_id):
        flag = True
        step = 50
        offset = 0
        access_token = self._get_access_token()
        result = []
        while flag:
            data = []
            r = requests.get(
                f"https://api.spotify.com/v1/artists/{artist_id}/albums",
                params={
                    "offset": offset,
                    "limit": step,
                    "access_token": access_token,
                },
            )

            data = r.json()
            if "error" in data and data["error"].get("status") == 429:
                wait_for_time = int(r.headers["Retry-After"]) + 2
                logging.info(f"Spotify Retry-After: {wait_for_time}")
                time.sleep(wait_for_time)
                continue

            if "items" not in data:
                logging.error(f"Spotify API error: {data}")
                raise KeyError("items")
            data = [item["id"] for item in data["items"]]
            if data:
                result += data
                offset += step
            else:
                flag = False
        return result

    def get_truck_names_for_album_id(self, album_id):
        flag = True
        step = 50
        offset = 0
        result = []
        access_token = self._get_access_token()
        while flag:
            data = []
            r = requests.get(
                f"https://api.spotify.com/v1/albums/{album_id}/tracks",
                params={
                    "offset": offset,
                    "limit": step,
                    "access_token": access_token,
                },
            )
            data = r.json()
            if "error" in data and data["error"].get("status") == 429:
                wait_for_time = int(r.headers["Retry-After"]) + 2
                logging.info(f"Spotify Retry-After: {wait_for_time}")
                time.sleep(wait_for_time)
                continue
            if "items" not in data:
                logging.error(f"Spotify API error: {data}")
                raise KeyError("items")
            data = [item["name"] for item in data["items"]]
            if data:
                result += data
                offset += step
            else:
                flag = False
        return result

    def get_artist_by_id(self, artist_id):
        """return (Name, Type, ListenersPerMonth, Img)"""
        access_token = self._get_access_token()
        r = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}",
            params={
                "access_token": access_token,
            },
        )
        data = r.json()
        img = requests.get(data["images"][0]["url"]).content
        return data["name"], data["type"], data["followers"]["total"], img

    def get_album_by_id(self, album_id):
        """return (Name, Type, TruckNumbers, ReleaseYear, Img)"""
        access_token = self._get_access_token()
        r = requests.get(
            f"https://api.spotify.com/v1/albums/{album_id}",
            params={
                "access_token": access_token,
            },
        )
        data = r.json()
        img = requests.get(data["images"][0]["url"]).content
        release_year = data['release_date'].split('-')[0]
        return data["name"], data["album_type"], data["tracks"]["total"], release_year, img
