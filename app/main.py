import logging
import os
import sys
import time
import signal
import traceback


from app.usecases import (
    DBCache,
    SpotifyManager,
    TelegramChanelManager,
    VkontakteClubManager,
    LastfmManager,
)

from app.entities import TelegramPost

INTERSECTION_THRESHOLD = 0.5


class App:
    def __init__(self):
        self.config = config = {}
        try:
            config["VK_KEY"] = os.environ["VK_KEY"]

            config["VC_CLUBS"] = os.environ["VC_CLUBS"].split(",")

            config["SP_KEY"] = os.environ["SP_KEY"]
            config["SP_CLIENT_ID"] = os.environ["SP_CLIENT_ID"]

            config["TG_KEY"] = os.environ["TG_KEY"]
            config["TG_CHAT"] = os.environ["TG_CHAT"]

            config["LF_KEY"] = os.environ["LF_KEY"]

            config["DB_NAME"] = os.environ["DB_NAME"]

        except KeyError as exc:
            logging.error(f"error in configuration {str(exc)};")
            self.config = None
            return

        logging.info(f"App config: {self.config};")

    def run(self):
        sm = SpotifyManager(self.config["SP_KEY"], self.config["SP_CLIENT_ID"])
        tgcm = TelegramChanelManager(
            self.config["TG_KEY"], self.config["TG_CHAT"], self.config["DB_NAME"]
        )
        lfm = LastfmManager(self.config["LF_KEY"])
        cache = DBCache(self.config["DB_NAME"])

        for club in self.config["VC_CLUBS"]:
            logging.info(f"start scaning vk club: {club};")

            vcm = VkontakteClubManager(self.config["VK_KEY"], club)

            for vk_album in vcm.albums:
                try:
                    logging.info(f"start looking for an Album: {vk_album};")

                    vk_album_hash = f"vk_album_{str(hash(vk_album))}"
                    if vk_album_hash in cache:
                        logging.info(f"Album is in the cache: {vk_album_hash};")
                        continue

                    match_sm_artist_id = None
                    match_sm_album_id = None

                    sm_artist_id = sm.get_artist_id_by_name(vk_album.artist)
                    if sm_artist_id is None:
                        logging.info(
                            f"artist with name {vk_album.artist} is not found in spotify;"
                        )
                        continue

                    match_sm_artist_id = sm_artist_id

                    logging.info(
                        f"artist {vk_album.artist} from vk is matched to {match_sm_artist_id} match_sm_artist_id;"
                    )

                    sm_albums = {}
                    sm_albums_ids = sm.get_albums_ids_by_artist_id(sm_artist_id)
                    for id_ in sm_albums_ids:
                        sm_albums[id_] = sm.get_truck_names_for_album_id(id_)

                    vk_tracks_set = set(vk_album.trucks)

                    for sm_album_id, sm_track_names in sm_albums.items():
                        sm_track_names_set = set(sm_track_names)
                        intersection_over_union = len(
                            vk_tracks_set & sm_track_names_set
                        ) / len(vk_tracks_set | sm_track_names_set)
                        if intersection_over_union >= INTERSECTION_THRESHOLD:
                            match_sm_album_id = sm_album_id
                            break

                    (
                        artist_name,
                        artist_type,
                        listeners_per_month,
                        artist_image,
                    ) = sm.get_artist_by_id(match_sm_artist_id)
                    if match_sm_album_id:
                        # IF ALBUM
                        (
                            album_name,
                            album_type,
                            truck_numbers,
                            release_year,
                            album_image,
                        ) = sm.get_album_by_id(match_sm_album_id)
                        tags = lfm.get_tags_for_albom(
                            artist=artist_name, album=album_name
                        )
                        if not tags:
                            tags = lfm.get_tags_for_artist(artist=artist_name)
                        post = TelegramPost(
                            image=album_image,
                            tags=tags[:5],
                            artist=artist_name,
                            spotify_url=f"https://open.spotify.com/album/{match_sm_album_id}",
                            album=album_name,
                            description=f'{album_type} · {truck_numbers} song{truck_numbers>1 and "s" or ""} · {release_year}',
                        )
                    else:
                        tags = lfm.get_tags_for_artist(artist=artist_name)
                        post = TelegramPost(
                            image=artist_image,
                            tags=tags[:5],
                            artist=artist_name,
                            spotify_url=f"https://open.spotify.com/artist/{match_sm_artist_id}",
                            description=f"{artist_type} · {listeners_per_month} monthly listeners",
                        )

                    tgcm.add_post(post)
                    cache.add(vk_album_hash)
                except BaseException as exc:
                    if isinstance(exc, SystemExit):
                        raise exc 
                    logging.error(exc)
                    traceback.print_exc()


interrupted = False


def signal_handler(signal, frame):
    global interrupted
    if interrupted:
        print("abort;")
        exit()
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)
SLEEP_TIME = 60 * 60

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    app = App()
    if app.config is None:
        print("exit with error;")
        exit(1)
    while True:
        app.run()
        if interrupted:
            print("Exit;")
            break
        print("sleep for an hour;")
        time.sleep(SLEEP_TIME)
