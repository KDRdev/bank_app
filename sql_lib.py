import sqlite3


class SqlHelper:
    """SQL commands wrapper class to simplify the code related to executing SQL commands."""
    
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)

    def execute(self, query, args=()):
        cursor = self.conn.cursor()
        res = cursor.execute(query, args)
        cursor.close()
        return True

    def insert(self, query, args=()):
        cursor = self.conn.cursor()
        if isinstance(args, list) and len(args) > 1:
            cursor.executemany(query, args)
        else:
            cursor.execute(query, args)
        self.conn.commit()
        cursor.close()
        return True

    def fetch_one(self, query, args=()):
        cursor = self.conn.cursor()
        res = cursor.execute(query, args).fetchone()
        cursor.close()
        return res

    def fetch_all(self, query, args=()):
        cursor = self.conn.cursor()
        res = cursor.execute(query, args).fetchall()
        cursor.close()
        return res
