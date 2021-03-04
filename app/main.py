import logging
import os
import sys
import time
import signal


from app.usecases import (DBCache,
                          SpotifyManager,
                          TelegramChanalManager,
                          VkontakteClubManager)

INTERSECTION_THRESHOLD = 0.5


class App:
    def __init__(self):
        self.config = config = {}
        try:
            config['VK_KEY'] = os.environ['VK_KEY']

            config['VC_CLUBS'] = os.environ['VC_CLUBS'].split(',')

            config['SP_KEY'] = os.environ['SP_KEY']
            config['SP_CLIENT_ID'] = os.environ['SP_CLIENT_ID']

            config['TG_KEY'] = os.environ['TG_KEY']
            config['TG_CHAT'] = os.environ['TG_CHAT']

            config['DB_NAME'] = os.environ['DB_NAME']
        except KeyError as exc:
            logging.error(f'error in configuration {str(exc)};')
            self.config = None
            return

        logging.info(f'App config: {self.config};')

    def run(self):
        sm = SpotifyManager(self.config['SP_KEY'], self.config['SP_CLIENT_ID'])
        tgcm = TelegramChanalManager(self.config['TG_KEY'], self.config['TG_CHAT'], self.config['DB_NAME'])
        cache = DBCache(self.config['DB_NAME'])

        for club in self.config['VC_CLUBS']:
            logging.info(f'start scaning vk club: {club};')

            vcm = VkontakteClubManager(self.config['VK_KEY'], club)

            for vk_albom in vcm.alboms:
                logging.info(f'start looking for an albom: {vk_albom};')

                vk_albom_hash = f'vk_albom_{str(hash(vk_albom))}'
                if vk_albom_hash in cache:
                    logging.info(f'albom is in the cache: {vk_albom_hash};')
                    continue

                match_sm_artist_id = None
                match_sm_album_id = None

                sm_artist_id = sm.get_artist_id_by_name(vk_albom.artist)
                if sm_artist_id is None:
                    logging.info(f'artist with name {vk_albom.artist} is not found in spotify;')
                    continue

                match_sm_artist_id = sm_artist_id

                logging.info(f'artist {vk_albom.artist} from vk is matched to {match_sm_artist_id} match_sm_artist_id;')

                sm_albums = {}
                sm_albums_ids = sm.get_albums_ids_by_artist_id(sm_artist_id)
                for id_ in sm_albums_ids:
                    sm_albums[id_] = sm.get_trak_names_for_album_id(id_)

                vk_tracks_set = set(vk_albom.traks)

                for sm_album_id, sm_track_names in sm_albums.items():
                    sm_track_names_set = set(sm_track_names)
                    intersection_over_union = len(
                        vk_tracks_set & sm_track_names_set)/len(vk_tracks_set | sm_track_names_set)
                    if intersection_over_union >= INTERSECTION_THRESHOLD:
                        match_sm_album_id = sm_album_id
                        break

                if match_sm_album_id:
                    tgcm.add_post(f'https://open.spotify.com/album/{match_sm_album_id}')
                else:
                    tgcm.add_post(f'https://open.spotify.com/artist/{match_sm_artist_id}')

                cache.add(vk_albom_hash)


interrupted = False


def signal_handler(signal, frame):
    global interrupted
    if interrupted:
        print('Abort;')
        exit()
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)
SLEEP_TIME = 60*60

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    app = App()
    if app.config is None:
        print("Exit with error;")
        exit(1)
    while True:
        app.run()
        if interrupted:
            print("Exit")
            break
        print('sleep for houer;')
        time.sleep(SLEEP_TIME)
