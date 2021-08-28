import datetime

import requests
from app.entities import Album
from bs4 import BeautifulSoup


class VkontakteClubManager:
    def __init__(self, key, club_id):
        self.key = key
        self.club_id = club_id
        self.albums = self.get_albums_from_api()

    def _get_alboms_from_audio(self, albums, attach):
        artist = attach["audio"]["artist"]
        title = attach["audio"]["title"]
        if artist in albums:
            albums[artist].append(title)
        else:
            albums[artist] = [title]

    def _get_alboms_from_playlist(self, albums, attach):
        r = requests.get(
            attach["link"]["url"],
            params={
                "access_token": self.key,
                "v": "5.131",
            },
        )
        if not r.ok:
            logging.warning(f"Can't get playlist {attach['link']['url']}")
            return
        bs = BeautifulSoup(r.text, "html.parser")
        for ai_label in bs.select(".AudioPlaylistRoot > .audio_item .ai_label"):
            title, _, artist = ai_label.children
            title = title.string
            artist = artist.string
            if artist in albums:
                albums[artist].append(title)
            else:
                albums[artist] = [title]

    def get_albums_from_api(self, limit=50):
        r = requests.get(
            "https://api.vk.com/method/wall.get",
            params={
                "access_token": self.key,
                "v": "5.130",
                "domain": self.club_id,
                "count": limit,
            },
        )
        items = r.json()["response"]["items"]
        result = []
        for item in items:
            item_date = datetime.datetime.utcfromtimestamp(item["date"])
            albums = {}  # dickt of lists there key - artist, and item of list - truck
            if "attachments" not in item:
                continue
            for attach in item["attachments"]:
                if (
                    attach["type"] == "link"
                    and attach["link"]["description"] == "Playlist"
                ):
                    self._get_alboms_from_playlist(albums, attach)
                elif attach["type"] == "audio":
                    self._get_alboms_from_audio(albums, attach)
                else:
                    continue
            if len(albums.keys()) != 1:
                continue
            for artist, trucks in albums.items():
                result.append(Album(artist=artist, trucks=tuple(trucks)))
        return result
