import dataclasses
import datetime
import typing


@dataclasses.dataclass
class TelegramPost:
    date: datetime.datetime
    text: str

    def __str__(self):
        return f'TelegramPost [{self.date}]: {self.text}'


@dataclasses.dataclass(eq=True, frozen=True)
class Albom:
    artist: str
    traks: typing.Tuple[str]

    def __str__(self):
        return f'Albom by {self.artist}: {self.traks[:3]}'
