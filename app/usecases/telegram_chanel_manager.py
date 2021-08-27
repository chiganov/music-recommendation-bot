import datetime
import logging
import sqlite3

import requests
from app.entities import TelegramPostModel, TelegramPost


class TelegramChanelManager:
    def __init__(self, key, chat_id, db_name):
        self.key = key
        self.chat_id = chat_id
        self.conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        # CRETE DB
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS posts 
                (
                id INTEGER PRIMARY KEY,
                date TIMESTAMP, 
                text TEXT
                );
                """)
        self.posts = self._get_posts_from_db()

    def _get_posts_from_db(self, limit=100):
        result = []
        with self.conn:
            result = self.conn.execute("""SELECT id, date, text FROM posts LIMIT (?);""", (limit,))
        return [TelegramPostModel(date=r[1], text=r[2]) for r in result]

    def _add_post_to_db(self, post):
        with self.conn:
            self.conn.execute("INSERT INTO posts(date, text) values (?, ?);", (post.date, post.text))

    def _get_post_by_text(self, text):
        with self.conn:
            result = self.conn.execute("SELECT id, date, text FROM posts WHERE text=(?);", (text,))
        data = result.fetchone()
        if data is None:
            return
        return TelegramPostModel(date=data[1], text=data[2])

    def _send_post_to_channel(self, post: TelegramPost):
        r = requests.post(
            f'https://api.telegram.org/bot{self.key}/sendPhoto',
            data={
                'parse_mode': 'html',
                'caption': post.get_html_text(),
                'chat_id': self.chat_id,
            },
            files={
                'photo': post.image
            }
        )
        return r.json().get('ok', False)

    def add_post(self, post: TelegramPost):
        text = post.get_html_text()
        if self._get_post_by_text(text) or self._get_post_by_text(post.spotify_url):
            logging.info('Post already exists')
            return
        db_post = TelegramPostModel(
            date=datetime.datetime.now(),
            text=text,
        )
        self._send_post_to_channel(post)
        self._add_post_to_db(db_post)
        self.posts.append(db_post)
