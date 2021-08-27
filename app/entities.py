import dataclasses
import datetime
import typing


@dataclasses.dataclass
class TelegramPost:
    image: typing.IO
    tags: typing.Tuple[str]
    artist: str
    spotify_url: str
    album: str = None
    description: str = None

    @staticmethod
    def _clean_html(s: str):
        return s.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

    def get_html_text(self):
        if self.album:
            title = self.album
            extra_title = self.artist
        else:
            title = self.artist
            extra_title = "Artist"
        tags = [tag for tag in self.tags if not tag.isnumeric()]
        tags = [f"#{tag.replace(' ', '').replace('-', '')}" for tag in tags]
        tags = [tag.lower() for tag in tags]
        tags = " ".join(tags)
        return f"""
<b>{self._clean_html(title)}</b>
{self._clean_html(extra_title)}
{self._clean_html(self.description)}

<a href='{self.spotify_url}'>Spotify Link</a>

{self._clean_html(tags)}
        """


@dataclasses.dataclass
class TelegramPostModel:
    date: datetime.datetime
    text: str

    def __str__(self):
        return f"TelegramPostModel [{self.date}]: {self.text}"


@dataclasses.dataclass(eq=True, frozen=True)
class Album:
    artist: str
    trucks: typing.Tuple[str]

    def __str__(self):
        return f"Album by {self.artist}: {self.trucks[:3]}"
