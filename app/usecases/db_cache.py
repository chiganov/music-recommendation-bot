import sqlite3
import datetime


class DBCache:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS cache
                (
                id INTEGER PRIMARY KEY,
                date TIMESTAMP,
                payload TEXT
                );
                """)

    def __contains__(self, payload):
        with self.conn:
            result = self.conn.execute("SELECT id FROM cache WHERE payload=(?);", (payload,))
        data = result.fetchone()
        if data:
            return True
        return False

    def add(self, payload):
        with self.conn:
            self.conn.execute(
                "INSERT INTO cache(date, payload) values (?, ?);",
                (datetime.datetime.now(), payload)
            )
